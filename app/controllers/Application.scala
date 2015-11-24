package controllers

import play.api._
import play.api.mvc._
import scala.sys.process._
import play.api.libs.json._

import java.io.File

class Application extends Controller {

   def downloadVideo(video_id : String): String = {
      val link: String = s"https://www.youtube.com/watch?v=$video_id"
      val download_string = s"youtube-dl --write-auto-sub --write-srt --sub-lang en -o /var/www/videos/$video_id.%(ext)s $link"
      download_string !

      val extensionSearch = "ls -l /var/www/videos" #| s"grep $video_id" !!

      val extensionRegex = """\.([^(en\.srt)]\w+)""".r
      val extension: Option[String] = for (
         c <- extensionRegex findFirstMatchIn extensionSearch
      ) yield (c group 1)

      extension match {
         case Some(ext) => ext
         case None => ""
      }
   }

   def extractFrames(video_id : String, extension: String): Float = {
      s"mkdir /var/www/frames/$video_id" !
      val frames = s"ffmpeg -i /var/www/videos/$video_id.$extension -r 1 /var/www/frames/$video_id/%d.png" !!
      val duration = s"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /var/www/videos/$video_id.$extension" !!

      duration.toFloat
   }

   def numFrames(video_id: String): Int = {
      val frames: String = s"ls /var/www/frames/$video_id" #| "wc -l" !!

      frames.trim.toInt
   }

   def totalFrames(video_id: String, duration: Float, extension: String): Float = {
      val fps = s"ffprobe /var/www/videos/$video_id.$extension -v 0 -select_streams v -print_format flat -show_entries stream=r_frame_rate" !!

      val fpsRegex = """(\d+)/(\d+)""".r
      val fpsReal: Option[Float] = for (
         c <- fpsRegex findFirstMatchIn fps
      ) yield ((c group 1).toFloat / (c group 2).toFloat)

      fpsReal match {
         case Some(f) => f * duration
         case None => 0
      }
   }

   def extractAudio(video_id: String, extension: String) {
      val extract_audio = s"ffmpeg -i /var/www/videos/$video_id.$extension -ab 160k -ac 2 -ar 44100 -vn /var/www/audio/$video_id.mp3" !!
   }

   def index(video_id : String) = Action{implicit request =>
      val extension = downloadVideo(video_id)
      val duration = extractFrames(video_id, extension)
      val frames = numFrames(video_id)
      val total_frames = totalFrames(video_id, duration, extension)
      val cap_exists = new java.io.File(s"/var/www/videos/$video_id.en.srt").exists

      extractAudio(video_id, extension)
      val audio_exists = new java.io.File(s"/var/www/audio/$video_id.mp3").exists

      val res = Json.obj(
        "num_frames" -> frames,
        "total_frames" -> total_frames.toInt,
        "duration" -> duration.toInt,
        "downloaded_caption" -> cap_exists,
        "extracted_audio" -> audio_exists
      )
      Ok(res)
   }
}
