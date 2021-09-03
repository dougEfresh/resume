resource "aws_acm_certificate" "cert" {
  domain_name       = "resume.dougchimento.com"
  validation_method = "DNS"
  lifecycle {
    create_before_destroy = true
  }
}
