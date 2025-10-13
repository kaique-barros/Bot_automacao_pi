import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USUARIO = "saulocardoso3557314@gmail.com"
SENHA = "Be2025ta$"
WAIT = 10

def main():
    """Acessa site GGmax já aberto no Chrome"""
    options = webdriver.ChromeOptions()
    options.debugger_address = "127.0.0.1:9222"  # porta padrao do --remote-debugging
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, WAIT)

    try:
        menu_icon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".icon-menu-03")))
        menu_icon.click()
        print("Menu aberto.")
    except Exception as e:
            print("Erro ao abrir menu:", e)
        
    try:
        entrar_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='account__popover']//a[contains(text(), 'Entrar')]")))
        entrar_link.click()
        print("Cliquei no botão 'Entrar'.")
    except Exception as e:
            print("Erro ao clicar no botão de entrar:", e)
        
    try:
        campo_email = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Usuário ou e-mail']")))
        campo_email.send_keys(USUARIO)
        print("E-mail preenchido.")
        campo_senha = driver.find_element(By.CSS_SELECTOR, "[name='password']")
        campo_senha.send_keys(SENHA)
        print("Senha preenchida.")
    except Exception as e:
            print("Erro ao preencher dados do usuário:", e)
        
    try:
        botao_entrar_login = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'form-login')]//button[contains(text(), 'Entrar')]")))
        botao_entrar_login.click()
        print("Cliquei no botão final de login.")
    except Exception as e:
            print("Erro ao clicar no botão de finalizar login:", e)

    # try:
    #     wait.until(EC.presence_of_element_located(()))
    #     print("Login realizado com sucesso!")
    # except Exception as e:
    #     print(f"Ocorreu um erro durante o processo de login: {e}")

    finally:
        pass

if __name__ == "__main__":
    main()