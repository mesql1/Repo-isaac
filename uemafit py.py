# UEMAFit - Sistema de Treinos (CRUD)
# Cadastra alunos e monta a ficha de treino de cada um com base na idade e na meta.

import json
import os

ARQUIVO = "alunos.json"  # onde os alunos ficam salvos entre uma execução e outra


class PersonalTrainer:

    def __init__(self):
        self.alunos = []
        self.proximo_id = 1
        self.carregar()

    # lê o arquivo json e recupera os alunos, se já tiver algum salvo
    def carregar(self):
        if os.path.exists(ARQUIVO):
            try:
                with open(ARQUIVO, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                self.alunos = dados["alunos"]
                self.proximo_id = dados["proximo_id"]
            except Exception:
                print("Não consegui ler o arquivo de dados, começando vazio.")

    # regrava o arquivo com a lista de alunos atual, chamada depois de qualquer alteração
    def salvar(self):
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump({"alunos": self.alunos, "proximo_id": self.proximo_id},
                      f, ensure_ascii=False, indent=2)

    # define o grupo do aluno pela idade
    def definir_grupo(self, idade):
        if idade <= 17:
            return "Adolescente"
        elif idade <= 59:
            return "Adulto"
        else:
            return "Idoso"

    # procura um aluno pelo nome (sem diferenciar maiúscula/minúscula e espaço), retorna None se não achar
    def buscar_aluno(self, nome):
        nome = nome.strip().lower()
        for aluno in self.alunos:
            if aluno["nome"].strip().lower() == nome:
                return aluno
        return None

    # monta a ficha base pelo grupo do aluno, depois soma um exercício extra de acordo com a meta
    def montar_ficha(self, grupo, meta):
        if grupo == "Adolescente":
            ficha = [
                "Treino funcional leve, sem sobrecarga",
                "Exercícios de coordenação e mobilidade",
                "Flexão, agachamento e prancha (peso do corpo)",
                "Cardio leve, 20 a 30 min"
            ]
        elif grupo == "Adulto":
            ficha = [
                "Musculação dividida (treino ABC)",
                "Agachamento, supino, remada, levantamento terra",
                "Cardio moderado/intenso, 30 a 40 min",
            ]
        else:  # Idoso
            ficha = [
                "Treino funcional de baixo impacto",
                "Cargas leves e mais repetições",
                "Exercícios de equilíbrio e mobilidade",
                "Caminhada ou bike, 15 a 25 min"
            ]

        # ajuste extra dependendo da meta que o aluno falou
        meta = meta.lower()
        if "emagrec" in meta:
            ficha.append("Extra: mais tempo de cardio pra ajudar na meta")
        elif "hipertrofia" in meta or "massa" in meta:
            ficha.append("Extra: aumentar carga e diminuir repetição")
        elif "resistência" in meta or "resistencia" in meta:
            ficha.append("Extra: circuito com pouco descanso entre séries")

        return ficha

    # CREATE - cadastra o aluno (com as validações) e já parte pra entrevista, pra montar a ficha na hora
    def cadastrar_aluno(self):
        print("\nCadastro de aluno")
        nome = input("Nome: ").strip()

        if nome == "":
            print("Nome não pode ficar em branco.")
            return

        if self.buscar_aluno(nome):
            print("Já tem um aluno com esse nome cadastrado.")
            return

        idade = input("Idade: ").strip()
        if not idade.isdigit() or int(idade) <= 0 or int(idade) > 120:
            print("Idade inválida, cadastro não realizado.")
            return
        idade = int(idade)

        dia = input("Dia disponível pra treinar: ").strip()
        if dia == "":
            print("Dia não pode ficar em branco.")
            return

        aluno = {
            "id": self.proximo_id,
            "nome": nome,
            "idade": idade,
            "dia": dia,
            "grupo": self.definir_grupo(idade),
            "meta": "",
            "ficha": []
        }
        self.proximo_id += 1

        self.alunos.append(aluno)
        self.salvar()
        print(f"Aluno {nome} cadastrado! Grupo: {aluno['grupo']}")

        print("Agora vamos fazer a entrevista rapidinho pra montar o treino.")
        self.entrevistar_aluno(nome)

    # READ - lista todos os alunos com os dados e a ficha (se já tiver sido montada)
    def visualizar_alunos(self):
        print("\nAlunos cadastrados:")

        if len(self.alunos) == 0:
            print("Ainda não tem nenhum aluno cadastrado.")
            return

        for aluno in self.alunos:
            print("-" * 30)
            print("Nome:", aluno["nome"])
            print("Idade:", aluno["idade"], f"({aluno['grupo']})")
            print("Dia disponível:", aluno["dia"])
            print("Meta:", aluno["meta"] if aluno["meta"] else "não informada")
            if aluno["ficha"]:
                print("Ficha de treino:")
                for exercicio in aluno["ficha"]:
                    print("  *", exercicio)
            else:
                print("Ficha de treino: ainda não montada")

    # UPDATE - troca idade e/ou dia do aluno; campo vazio mantém o valor que já tinha
    def atualizar_aluno(self):
        nome = input("\nNome do aluno que quer atualizar: ").strip()
        aluno = self.buscar_aluno(nome)

        if aluno is None:
            print("Não achei esse aluno.")
            return

        print("Aperta enter se não quiser mudar o campo.")

        nova_idade = input(f"Idade ({aluno['idade']}): ").strip()
        if nova_idade != "":
            if nova_idade.isdigit() and 0 < int(nova_idade) <= 120:
                aluno["idade"] = int(nova_idade)
                aluno["grupo"] = self.definir_grupo(aluno["idade"])
            else:
                print("Idade inválida, não foi alterada.")

        novo_dia = input(f"Dia disponível ({aluno['dia']}): ").strip()
        if novo_dia != "":
            aluno["dia"] = novo_dia

        resposta = input(
            "Quer refazer a ficha de treino? (s/n): ").strip().lower()
        if resposta == "s":
            self.entrevistar_aluno(aluno["nome"])

        self.salvar()
        print("Atualizado com sucesso.")

    # DELETE - remove o aluno, mas só depois de confirmar com o usuário
    def remover_aluno(self):
        nome = input("\nNome do aluno que quer remover: ").strip()
        aluno = self.buscar_aluno(nome)

        if aluno is None:
            print("Não achei esse aluno.")
            return

        confirma = input(
            f"Tem certeza que quer remover {aluno['nome']}? (s/n): ").strip().lower()
        if confirma == "s":
            self.alunos.remove(aluno)
            self.salvar()
            print("Aluno removido.")
        else:
            print("Ok, cancelado.")

    # pergunta a meta do aluno e monta a ficha combinando ela com o grupo dele
    def entrevistar_aluno(self, nome=None):
        if nome is None:
            nome = input("\nNome do aluno pra entrevistar: ").strip()

        aluno = self.buscar_aluno(nome)
        if aluno is None:
            print("Não achei esse aluno.")
            return

        meta = input(
            f"Qual a meta de treino do {aluno['nome']}? (emagrecimento, hipertrofia, resistência...): ").strip()
        if meta == "":
            print("Meta não pode ficar em branco.")
            return

        aluno["meta"] = meta
        aluno["ficha"] = self.montar_ficha(aluno["grupo"], meta)
        self.salvar()

        print(f"\nFicha montada pra {aluno['nome']} ({aluno['grupo']}):")
        for exercicio in aluno["ficha"]:
            print(" -", exercicio)


# mostra o menu em loop e chama a função certa de acordo com a opção escolhida
def main():
    trainer = PersonalTrainer()

    while True:
        try:
            print("\n===== UEMAFit - Sistema de Treinos =====")
            print("1 - Cadastrar aluno")
            print("2 - Ver alunos cadastrados")
            print("3 - Atualizar aluno")
            print("4 - Remover aluno")
            print("5 - Entrevistar aluno / refazer ficha")
            print("0 - Sair")

            opcao = input("Escolha: ").strip()

            if opcao == "1":
                trainer.cadastrar_aluno()
            elif opcao == "2":
                trainer.visualizar_alunos()
            elif opcao == "3":
                trainer.atualizar_aluno()
            elif opcao == "4":
                trainer.remover_aluno()
            elif opcao == "5":
                trainer.entrevistar_aluno()
            elif opcao == "0":
                print("Saindo do sistema...")
                break
            else:
                print("Opção inválida, tenta de novo.")

        except (KeyboardInterrupt, EOFError):
            # evita mostrar erro feio se o usuário sair no meio de um input (Ctrl+C, por exemplo)
            print("\nSaindo do sistema...")
            break


if __name__ == "__main__":
    main()
