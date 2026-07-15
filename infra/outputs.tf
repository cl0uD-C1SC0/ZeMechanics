output "kubeconfig_path" {
  description = "Caminho do kubeconfig gerado para o cluster Kind"
  value       = kind_cluster.this.kubeconfig_path
}

output "api_url" {
  description = "URL da API exposta via NodePort"
  value       = "http://localhost:30080"
}

output "maildev_ui_url" {
  description = "URL da interface web do MailDev"
  value       = "http://localhost:30081"
}
