import re

# Func que valida CPF
def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        print("> CPF Inválido, tente novamente..")
        return False
    
    if cpf == cpf[0] * 11:
        print("> CPF Inválido, tente novamente..")
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    digito1 = 0 if resto == 10 else resto

    if digito1 != int(cpf[9]):
        print("> CPF Inválido, tente novamente..")
        return False

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    digito2 = 0 if resto == 10 else resto

    if digito2 != int(cpf[10]):
        print("> CPF Inválido, tente novamente..")
        return False
    
    print("> CPF Válido!")
    return True

# Func que valida CNPJ

# Func que valida se o Cliente ja esta cadastrado