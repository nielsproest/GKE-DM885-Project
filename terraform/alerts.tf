resource "google_monitoring_alert_policy" "alert_policy" {
  display_name = "Request Latency [3000 ms]"
  combiner     = "OR"
  conditions {
      display_name = "Consumed API - Request latencies"
      condition_threshold {
        comparison = "COMPARISON_GT"
        duration = "0s"
        filter = "resource.type=\"consumed_api\" AND metric.type=\"serviceruntime.googleapis.com/api/request_latencies\""
        threshold_value= "3"
        trigger {
          count = "1"
        }
        aggregations {
            alignment_period = "300s"
            per_series_aligner = "ALIGN_PERCENTILE_99"
        }
      }
  }
}


resource "google_monitoring_alert_policy" "extra_alert_policy" {
  display_name = "Rate quota usage [85]"
  combiner     = "OR"
  conditions {
      display_name = "Consumer Quota - Rate quota usage"
      condition_threshold {
        comparison = "COMPARISON_GT"
        duration = "0s"
        filter = "resource.type=\"consumer_quota\" AND metric.type=\"serviceruntime.googleapis.com/quota/rate/net_usage\""
        threshold_value= "85"
        trigger {
          count = "1"
        }
        aggregations {
            alignment_period = "300s"
            per_series_aligner = "ALIGN_MAX"
        }
      }
  }
}

resource "google_monitoring_alert_policy" "cpu_alert_policy" {
  display_name = "Kubernetes Container - CPU limit utilization [85]"
  combiner     = "OR"
  conditions {
      display_name = "Kubernetes Container - CPU limit utilization"
      condition_threshold {
        comparison = "COMPARISON_GT"
        duration = "0s"
        filter = "resource.type=\"consumer_quota\" AND metric.type=\"serviceruntime.googleapis.com/quota/rate/net_usage\""
        threshold_value= "75"
        trigger {
          count = "1"
        }
        aggregations {
            alignment_period = "300s"
            per_series_aligner = "ALIGN_MEAN"
        }
      }
  }
}