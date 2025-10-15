import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BuyProccesss():
    def __init__(self, name, wait, price):
        self.NOME = name
        self.WAIT = wait
        self.PRICE = price
        self.pix_codes = []
    
    def generate_fake_cpf(self, formatted=True):
        def calc_digit(digs):
            # digs: lista de chars (ex: ['1','2',...])
            if len(digs) == 9:
                weights = list(range(10, 1, -1))
            else:
                weights = list(range(11, 1, -1)) 
            s = sum(int(d) * w for d, w in zip(digs, weights))
            r = s % 11
            return '0' if r < 2 else str(11 - r)

        n = [str(random.randint(0, 9)) for _ in range(9)]
        n.append(calc_digit(n))
        n.append(calc_digit(n))
        cpf = ''.join(n)
        if formatted:
            return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
        return cpf

    def set_contenteditable_text(self, driver, elem, text):
        try:
            driver.execute_script("""
                arguments[0].focus();
                arguments[0].innerText = arguments[1];
                arguments[0].dispatchEvent(new Event('input', {bubbles:true}));
                arguments[0].dispatchEvent(new Event('change', {bubbles:true}));
            """, elem, text)
            return True
        except Exception:
            # fallback: tentar enviar keys (alguns editors aceitam)
            try:
                elem.click()
                elem.clear()
                elem.send_keys(text)
                return True
            except Exception:
                return False

    def buy(self):
        # Conectar ao Chrome remoto (a aba já aberta)
        options = webdriver.ChromeOptions()
        options.debugger_address = "127.0.0.1:9222"  # porta do --remote-debugging
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, self.WAIT)

        try:
            time.sleep(1.5) 
            try:
                filter_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".filter__button")))
                filter_btn.click()
                print("[*] Cliquei no botão 'Escolha um item'.")
            except Exception as e:
                print("[!] Erro ao clicar no botão do popover:", e)

            popover_container = None
            try:
                popover_container = wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".announcement-item--single-select__popover"))
                )
                time.sleep(0.25)
                print("[*] Popover visível.")
            except Exception as e:
                print("[!] Erro ao esperar pelo popover:", e)

            options_list = []
            if popover_container:
                options_list = popover_container.find_elements(By.CSS_SELECTOR, ".popover__option")
            print(f"[*] Encontrei {len(options_list)} opções no popover.")

            clicked_option = False
            for opt in options_list:
                try:
                    price_elem = opt.find_element(By.CSS_SELECTOR, ".option__price")
                except:
                    price_elem = None
                    ## ONDE DEVE-SE ADICIONAR O VALOR DO PRODUTO QUE SE DESEJA COMPRAR, COMO NO CASO ESTÁ 29,90. 
                    # PARA MUDAR, BASTA ALTERAR PARA O VALOR DESEJADO EM AMBOS OS "29,90" E "29.90" ABAIXO:
                if price_elem and (self.PRICE == price_elem.text or self.PRICE.replace(",", ".") == price_elem.text):
                    opt.click()
                    clicked_option = True
                    print(f"[*] Opção com preço {price_elem.text} selecionada!")
                    break

            if not clicked_option and options_list:
                options_list[0].click()
                print("[!] Fallback: selecionei a primeira opção.")

            time.sleep(0.6)

            try:
                buy = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-addcart")))
                buy.click()
                print("[*] Clicado em 'Adicionar ao carrinho' / comprar.")
            except Exception:
                print("[*] Não conseguiu clicar em '.btn-addcart' — verifique o seletor.")

            time.sleep(0.6)

            # FINALIZANDO A COMPRA
            try:
                finalizar = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//*[contains(@class,'buy__button') and contains(@class,'btn')]")
                ))
                finalizar.click()
                print("[*] Clicado em 'Finalizar compra'.")
            except Exception:
                try:
                    btn_text = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(normalize-space(.),'Finalizar compra')]")
                    ))
                    btn_text.click()
                    print("[*] Clicado no botão com texto 'Finalizar compra'.")
                except Exception:
                    print("[*] Não consegui finalizar compra automaticamente.")

            time.sleep(0.6)

            # PARA NAO TER NENHUM PLANO ADICIONAL NO MOMENTO DA COMPRA
            try:
                prosseguir = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(normalize-space(.),'Prosseguir sem plano adicional')]")))
                prosseguir.click()
                print("[*] Prosseguiu sem plano adicional.")
            except Exception:
                try:
                    fallback = driver.find_element(By.CSS_SELECTOR, "a.btn.btn-dark")
                    fallback.click()
                    print("[!] Fallback: cliquei em a.btn.btn-dark")
                except Exception:
                    print("[!] Não encontrei 'Prosseguir sem plano adicional'.")

            time.sleep(0.6)

            # PAGAMENTO VIA PIX
            try:
                pix = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".gg-payment-method.pix")))
                pix.click()
                print("[*] Selecionado método Pix.")
            except Exception:
                try:
                    pix2 = driver.find_element(By.XPATH, "//*[contains(normalize-space(.),'Pix')]")
                    pix2.click()
                    print("[*] Selecionado Pix por texto.")
                except Exception:
                    print("[!] Não consegui selecionar Pix.")

            time.sleep(0.6)

            # PROCESSO DO PIX ADD NOME
            name_filled = False
            try:
                nome_input = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[@placeholder='Digite o seu nome completo']")
                ))

                nome_input.click()
                nome_input.clear()
                nome_input.send_keys(self.NOME)
                
                name_filled = True
            except Exception as e:
                print(f"[!] Erro ao tentar preencher o nome no campo <input>: {e}")
                name_filled = False

            if name_filled:
                print("[*] Nome preenchido com sucesso.")
            else:
                print("[!] Não consegui preencher o nome automaticamente.")

            time.sleep(0.4)


            # GERANDO O CPF E PREENCHENDO PARA CONCLUIR A SOLICITAÇÃO DA CHAVE PIX
            fake_cpf = self.generate_fake_cpf(formatted=True)
            cpf_filled = False
            try:
                cpf_span = driver.find_element(By.XPATH, "//span[contains(normalize-space(.),'CPF')]")
                cpf_edit = cpf_span.find_element(By.XPATH, "following::div[@contenteditable][1]")
                cpf_filled = self.set_contenteditable_text(driver, cpf_edit, fake_cpf)
            except Exception:
                try:
                    inp = driver.find_element(By.CSS_SELECTOR, "input[data-maska-value], input[placeholder*='#']")
                    driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input')); arguments[0].dispatchEvent(new Event('change'));", inp, fake_cpf)
                    cpf_filled = True
                except Exception:
                    cpf_filled = False

            if cpf_filled:
                print("[*] CPF (teste) gerado e preenchido:", fake_cpf)
            else:
                print("[!] Não consegui preencher o CPF automaticamente. Gerado:", fake_cpf)

            time.sleep(0.4)

            # GERANDO O QRCODE APÓS O PREENCHIMENTO
            try:
                gerar = driver.find_element(By.XPATH, "//button[contains(normalize-space(.),'Gerar QRCode')]")
                gerar.click()
                print("[*] Clicado em 'Gerar QRCode'.")
            except Exception:
                try:
                    gerar = driver.find_element(By.XPATH, "//button[contains(normalize-space(.),'Gerar QRCode e copia/cola')]")
                    gerar.click()
                    print("[*] Clicado em 'Gerar QRCode e copia/cola'.")
                except Exception:
                    print("[!] Não achei o botão 'Gerar QRCode'.")

            time.sleep(2.0)


            self.pix_code = "" 
            try:
                pix_input_field = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "div.pix-copy-input-container input")
                ))
                
                self.pix_code = pix_input_field.get_attribute('value')
                
                if self.pix_code:
                    print("[*] Código Pix copiado com sucesso!")
                    print(f"-> {self.pix_code[:180]}...") 
                    self.pix_codes.append(self.pix_code)
                else:
                    print("[!] ERRO: O campo de input do Pix foi encontrado, mas está vazio.")

            except Exception as e:
                print(f"[!] ERRO: Não foi possível encontrar ou copiar o código Pix. Detalhes: {e}")
            
            
        finally:
            # Mantemos aberto
            pass