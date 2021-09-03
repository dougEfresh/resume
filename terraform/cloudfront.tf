// Capture the certificate
//data "aws_acm_certificate" "cert" {
//  domain      = resume.dougchimento.com
//  most_recent = true
//}

// Create CF distribution with the captured certification
resource "aws_cloudfront_distribution" "domain_distribution" {
  origin {
    custom_origin_config {
      http_port              = "80"
      https_port             = "443"
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1", "TLSv1.1", "TLSv1.2"]
    }

    // Endpoint
    domain_name = aws_s3_bucket.website.website_endpoint
    origin_id   = "resume.dougchimento.com"
  }

  enabled             = true
    is_ipv6_enabled     = true
  default_root_object = "index.html"

  default_cache_behavior {
    viewer_protocol_policy = "redirect-to-https"
    compress               = true
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "resume.dougchimento.com"
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  // Alias
  aliases = ["resume.dougchimento.com"]

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  // Certification goes here
  viewer_certificate {
    acm_certificate_arn = "arn:aws:acm:us-east-1:841424144106:certificate/b7ade8c0-7cd3-4c9d-8b61-5f3db9f0c54c"
    ssl_support_method  = "sni-only"
  }
}
