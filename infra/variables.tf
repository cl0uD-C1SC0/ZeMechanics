variable "cluster_name" {
  description = "Nome do cluster Kind"
  type        = string
  default     = "zemechanics"
}

variable "manifests_path" {
  description = "Caminho para a pasta k8s/ com os manifestos do projeto"
  type        = string
  default     = "../k8s"
}
