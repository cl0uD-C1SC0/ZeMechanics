module "zemechanics" {
  source = "./modules/ze_mechanics"
 
  vpc_name         = "ze-mechanics-vpc"
  vpc_cidr         = "10.0.0.0/16"
  cluster_name     = "zemechanics-cluster"
  nodegroup_name   = "zemechanics-ndg-01"
  aws_iam_user_arn = "arn:aws:iam::277375108712:user/cloud_user" # ARN do seu usuario AWS com roles do EKS/ECR/Pipelines
}