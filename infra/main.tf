terraform {
  required_version = ">= 1.5"

  required_providers {
    kind = {
      source  = "tehcyx/kind"
      version = "~> 0.4"
    }
    kubectl = {
      source  = "alekc/kubectl"
      version = "~> 2.0"
    }
  }
}

# Cluster Kind com as portas 30080 (API) e 30081 (MailDev web UI) publicadas
# no host, já que o Kind não expõe NodePort automaticamente pra fora do
# container do node — precisa de extraPortMappings.
resource "kind_cluster" "this" {
  name           = var.cluster_name
  wait_for_ready = true

  kind_config {
    kind        = "Cluster"
    api_version = "kind.x-k8s.io/v1alpha4"

    node {
      role = "control-plane"

      extra_mounts {
        host_path      = abspath("${path.module}/data/mysql")
        container_path = "/mnt/data/mysql"
      }

      extra_port_mappings {
        container_port = 30080
        host_port      = 30080
      }

      extra_port_mappings {
        container_port = 30081
        host_port      = 30081
      }
    }
  }
}

# Este provider depende de atributos que só existem depois que o kind_cluster
# for criado. Na primeira aplicação, isso quebra se rodado num "terraform apply"
# só, porque o Terraform configura os providers antes de criar os recursos.
# Por isso o apply deve ser feito em duas etapas:
#   1) terraform apply -target=kind_cluster.this   (cria só o cluster)
#   2) terraform apply                              (aplica o restante)
provider "kubectl" {
  host                   = kind_cluster.this.endpoint
  cluster_ca_certificate = kind_cluster.this.cluster_ca_certificate
  client_certificate     = kind_cluster.this.client_certificate
  client_key             = kind_cluster.this.client_key
  load_config_file       = false
}
