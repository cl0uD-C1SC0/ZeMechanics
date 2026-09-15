terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.4"
}

# auth
provider "kubernetes" {
  host                   = module.zemechanics.cluster_endpoint
  cluster_ca_certificate = base64decode(module.zemechanics.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    args        = ["eks", "get-token", "--cluster-name", module.zemechanics.cluster_name]
    command     = "aws"
  }
}

provider "aws" {}