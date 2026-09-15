# ELASTIC CONTAINER REGISTRY
resource "aws_ecr_repository" "ecr" {
  name                 = "zemechanics"
  image_tag_mutability = "MUTABLE"

}


