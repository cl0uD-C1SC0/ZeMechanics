output "cluster_endpoint" {
  value = aws_eks_cluster.zemechanics-cluster.endpoint
}

output "cluster_certificate_authority_data" {
  value = aws_eks_cluster.zemechanics-cluster.certificate_authority[0].data
}

output "cluster_name" {
  value = aws_eks_cluster.zemechanics-cluster.name
}

output "ecr_url" {
  value = aws_ecr_repository.ecr.repository_url
}