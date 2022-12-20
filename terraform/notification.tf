resource "google_monitoring_notification_channel" "basic" {
  display_name = "Solveit Email Notification Channel"
  type         = "email"
  labels = {
    email_address = "frederikxyz@hotmail.com"
  }
  force_delete = false
}
