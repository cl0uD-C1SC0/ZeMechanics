locals {
  mysql_files   = fileset("${var.manifests_path}/mysql", "*.yaml")
  maildev_files = fileset("${var.manifests_path}/maildev", "*.yaml")
  api_files     = fileset("${var.manifests_path}/api", "*.yaml")
}

resource "kubectl_manifest" "namespace" {
  yaml_body = file("${var.manifests_path}/namespace.yaml")
}

resource "kubectl_manifest" "mysql" {
  for_each   = local.mysql_files
  yaml_body  = file("${var.manifests_path}/mysql/${each.value}")
  depends_on = [kubectl_manifest.namespace]
}

resource "kubectl_manifest" "maildev" {
  for_each   = local.maildev_files
  yaml_body  = file("${var.manifests_path}/maildev/${each.value}")
  depends_on = [kubectl_manifest.namespace]
}

# A API só é aplicada depois que mysql e maildev já subiram, como pedido.
resource "kubectl_manifest" "api" {
  for_each   = local.api_files
  yaml_body  = file("${var.manifests_path}/api/${each.value}")
  depends_on = [kubectl_manifest.mysql, kubectl_manifest.maildev]
}
