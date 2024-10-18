from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

URL = "https://cedulaprofesional.sep.gob.mx/cedula/presidencia/indexAvanzada.action"

def startDriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Necessary for Windows
    chrome_options.add_argument("--no-sandbox")  # Necessary for Linux
    chrome_options.add_argument("--disable-dev-shm-usage")  # Necessary for Linux

    driver = webdriver.Chrome(options=chrome_options)  # Pass options to the driver
    return driver

def navigatePage(driver):
    driver.get(URL)

def filloutForm(driver, user):
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'nombre')))
        driver.find_element(By.ID, 'nombre').send_keys(user.first_name)  # First name
        driver.find_element(By.ID, 'paterno').send_keys(user.last_name_father)  # Father's last name
        driver.find_element(By.ID, 'materno').send_keys(user.last_name_mother)  # Mother's last name
    except Exception as e:
        print(f"Error filling out the form: {e}")

def defClickConsult(driver):
    consultar_span = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'dijit_form_Button_0_label'))
    )
    consultar_span.click()

def extractResults(driver, license):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'tab2')))
    tab2 = driver.find_element(By.ID, 'tab2')
    rows = tab2.find_elements(By.CSS_SELECTOR, 'tr')
    resultados = []
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, 'td')
        if len(cells) >= 5:
            cedula = cells[0].text
            if cedula == license:
                resultado = {
                    'Cédula': cedula,
                    'Nombre': cells[1].text,
                    'Primer apellido': cells[2].text,
                    'Segundo apellido': cells[3].text,
                    'Tipo': cells[4].text
                }
                resultados.append(resultado)
    return resultados

def selectRowById(driver, license):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'tab2')))
    tab2 = driver.find_element(By.ID, 'tab2')
    rows = tab2.find_elements(By.CSS_SELECTOR, 'tr')
    for row in rows:
        cells = row.find_elements(By.CSS_SELECTOR, 'td')
        if len(cells) >= 5:
            cedula = cells[0].text
            if cedula == license:
                try:
                    cells[0].click()
                    return True
                except Exception as e:
                    print(f"Error clicking on the row: {e}")
                    return False
    return False

def extractDataDetails(driver):
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'tab3')))
        datos = {
            "Cédula": driver.find_element(By.ID, "detalleCedula").text,
            "Género": driver.find_element(By.ID, "detalleGenero").text,
            "Profesión": driver.find_element(By.ID, "detalleProfesion").text,
            "Año de expedición": driver.find_element(By.ID, "detalleFecha").text,
            "Institución": driver.find_element(By.ID, "detalleInstitucion").text,
        }
        return datos
    except Exception as e:
        print(f"Error extracting detail data: {e}")
        return {}

def closedriver(driver):
    driver.quit()
