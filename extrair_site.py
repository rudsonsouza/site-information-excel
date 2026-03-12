import time  
import sys  
import pandas as pd  
from selenium import webdriver  
from selenium.webdriver.chrome.service import Service  
from selenium.webdriver.chrome.options import Options  
from selenium.webdriver.common.by import By  
from selenium.webdriver.support.ui import WebDriverWait  
from selenium.webdriver.support import expected_conditions as EC  
from webdriver_manager.chrome import ChromeDriverManager  
from bs4 import BeautifulSoup  
  
  
def criar_driver():  
    """Cria e configura o driver do Chrome."""  
    options = Options()  
    options.add_argument("--headless")  # Remove esta linha se quiser ver o navegador  
    options.add_argument("--no-sandbox")  
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--window-size=1920,1080")  
    service = Service(ChromeDriverManager().install())  
    return webdriver.Chrome(service=service, options=options)  
  
  
def extrair_tabela(driver):  
    """Extrai os dados da tabela visível na página atual."""  
    soup = BeautifulSoup(driver.page_source, "html.parser")  
    tabelas = soup.find_all("table")  
    if not tabelas:  
        return [], []  
  
    # Pega a maior tabela (provavelmente a de dados)  
    tabela = max(tabelas, key=lambda t: len(t.find_all("tr")))  
  
    # Extrai cabeçalhos  
    headers = []  
    header_row = tabela.find("thead")  
    if header_row:  
        headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]  
    else:  
        first_row = tabela.find("tr")  
        if first_row:  
            headers = [cell.get_text(strip=True) for cell in first_row.find_all(["th", "td"])]  
  
    # Extrai linhas de dados  
    rows = []  
    tbody = tabela.find("tbody") or tabela  
    for tr in tbody.find_all("tr"):  
        cells = [td.get_text(strip=True) for td in tr.find_all(["td"])]  
        if cells and len(cells) > 1:  
            rows.append(cells)  
  
    return headers, rows  
  
  
def clicar_aba_lista_endereco(driver):  
    """Tenta clicar na aba 'lista endereço'."""  
    wait = WebDriverWait(driver, 20)  
      
    # Tenta diferentes seletores comuns para abas  
    seletores = [  
        "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'lista')]",  
        "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'lista')]",  
        "//li[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'lista')]",  
        "//span[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'lista')]",  
        "//div[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'lista')]",  
        "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'endere')]",  
    ]  
      
    for seletor in seletores:  
        try:  
            elemento = wait.until(EC.element_to_be_clickable((By.XPATH, seletor)))  
            elemento.click()  
            print(f"  Aba encontrada com seletor: {seletor}")  
            time.sleep(3)  
            return True  
        except Exception:  
            continue  
      
    return False  
  
  
def clicar_proxima_pagina(driver, pagina_atual):  
    """Tenta clicar no botão de próxima página."""  
    seletores_proximo = [  
        # Botão "próximo" ou "next"  
        "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'próx')]",  
        "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'next')]",  
        "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'próx')]",  
        # Botão com ícone de seta  
        "//a[contains(@class,'next')]",  
        "//li[contains(@class,'next')]/a",  
        "//button[contains(@class,'next')]",  
        # Número da próxima página  
        f"//a[text()='{pagina_atual + 1}']",  
        f"//button[text()='{pagina_atual + 1}']",  
        f"//li/a[text()='{pagina_atual + 1}']",  
        # Seta ">"  
        "//a[text()='›']",  
        "//a[text()='>']",  
        "//a[text()='»']",  
        "//button[text()='›']",  
    ]  
      
    for seletor in seletores_proximo:  
        try:  
            elemento = driver.find_element(By.XPATH, seletor)  
            if elemento.is_displayed() and elemento.is_enabled():  
                elemento.click()  
                time.sleep(2)  
                return True  
        except Exception:  
            continue  
      
    return False  
  
  
def main():  
    url = "https://cievs.saude.sp.gov.br/soro/"  
    total_paginas = 25  
    arquivo_saida = "lista_endereco_cievs.xlsx"  
      
    print(f"Iniciando extração de {url}")  
    print(f"Páginas esperadas: {total_paginas}")  
    print("-" * 60)  
      
    driver = criar_driver()  
    todos_dados = []  
    headers = []  
      
    try:  
        # 1. Acessar o site  
        print("Acessando o site...")  
        driver.get(url)  
        time.sleep(5)  
          
        # 2. Clicar na aba "lista endereço"  
        print("Procurando aba 'lista endereço'...")  
        if not clicar_aba_lista_endereco(driver):  
            print("AVISO: Não foi possível encontrar a aba automaticamente.")  
            print("Tentando extrair dados da página atual...")  
          
        time.sleep(3)  
          
        # 3. Extrair dados de cada página  
        for pagina in range(1, total_paginas + 1):  
            print(f"Extraindo página {pagina}/{total_paginas}...")  
              
            h, rows = extrair_tabela(driver)  
              
            if h and not headers:  
                headers = h  
                print(f"  Colunas encontradas: {headers}")  
              
            if rows:  
                todos_dados.extend(rows)  
                print(f"  {len(rows)} registros extraídos (total: {len(todos_dados)})")  
            else:  
                print(f"  Nenhum registro encontrado na página {pagina}")  
              
            # Avançar para próxima página (exceto na última)  
            if pagina < total_paginas:  
                if not clicar_proxima_pagina(driver, pagina):  
                    print(f"  Não foi possível avançar após página {pagina}. Encerrando.")  
                    break  
                time.sleep(2)  
          
    except Exception as e:  
        print(f"Erro durante a extração: {e}")  
        # Salva screenshot para debug  
        driver.save_screenshot("erro_debug.png")  
        print("Screenshot salvo em 'erro_debug.png' para debug.")  
    finally:  
        driver.quit()  
      
    # 4. Gerar Excel  
    if todos_dados:  
        # Ajusta headers se necessário  
        if headers and len(headers) != len(todos_dados[0]):  
            headers = [f"Coluna_{i+1}" for i in range(len(todos_dados[0]))]  
        elif not headers:  
            headers = [f"Coluna_{i+1}" for i in range(len(todos_dados[0]))]  
          
        df = pd.DataFrame(todos_dados, columns=headers)  
        df.to_excel(arquivo_saida, index=False, engine="openpyxl")  
        print("-" * 60)  
        print(f"Arquivo gerado: {arquivo_saida}")  
        print(f"Total de registros: {len(df)}")  
        print(f"Colunas: {list(df.columns)}")  
        print(f"\nPrimeiros 5 registros:")  
        print(df.head().to_string())  
    else:  
        print("Nenhum dado foi extraído. Verifique o site manualmente.")  
        print("Dicas:")  
        print("  1. Remova '--headless' da função criar_driver() para ver o navegador")  
        print("  2. Verifique se o site está acessível")  
        print("  3. Veja o screenshot 'erro_debug.png' se existir")  
        sys.exit(1)  
  
  
if __name__ == "__main__":  
    main()