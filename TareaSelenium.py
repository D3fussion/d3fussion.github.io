from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import time
from get_db_connection import get_db_connection
from selenium.webdriver.chrome.options import Options

urlPagina = 'http://localhost:3000'


def update_values(driver, no_products=False):
    global product_list, product
    product_list = driver.find_element(By.ID, "elementosCarrito")
    if not no_products:
        product = product_list.find_element(By.CSS_SELECTOR, "div:first-child")


def add_product(driver, first_time, x):
    global product_id, stock
    if first_time:
        driver.find_element(By.ID, "aquiVanLosProductos").find_elements(By.TAG_NAME, "div")[0].find_element(By.TAG_NAME,
                                                                                                            "a").click()
        time.sleep(4 * x)

        product_id = driver.current_url.split("$codigo=")[1]

        driver.find_element(By.ID, "datos_adicionales").click()
        time.sleep(2 * x)

        stock = int(driver.find_element(By.TAG_NAME, "strong").text[7:])

        print(f"El id del producto que se probara es: {product_id}, con un stock de {stock}")
    else:
        driver.get(f"{urlPagina}/artic.html?$codigo={product_id}")
        time.sleep(3 * x)

    add_to_cart = driver.find_element(By.ID, "add-to-cart")
    time.sleep(3 * x)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(3 * x)
    add_to_cart.click()

    time.sleep(2 * x)
    driver.find_element(By.CSS_SELECTOR, "button[class='u-dialog-close-button u-icon u-text-grey-40 u-icon-2']").click()
    time.sleep(1 * x)

    driver.find_element(By.CSS_SELECTOR, "span[class='u-file-icon u-icon u-text-white u-icon-1']").click()

    print("Entrando al carrito...")
    time.sleep(3 * x)


def test_1(driver, x):
    global apply, prices
    update_values(driver)
    prices = dict()
    prices["before"] = product.find_element(By.CSS_SELECTOR,
                                            "p[class='u-align-center u-text u-text-default u-text-13']").text

    number_box = product.find_element(By.TAG_NAME, "input")
    number = number_box.get_attribute("value")
    number_box.clear()
    number_box.send_keys(str(int(number) + 1))
    time.sleep(1 * x)

    apply = driver.find_element(By.CSS_SELECTOR,
                                "a[class='u-align-center-xs u-btn u-button-style u-custom-color-2 u-btn-1']")
    apply.click()
    time.sleep(2 * x)

    update_values(driver)
    prices["after"] = product.find_element(By.CSS_SELECTOR,
                                           "p[class='u-align-center u-text u-text-default u-text-13']").text

    print(
        f"El precio del producto antes es igual a: {prices['before']}\nDespues de sumarle 1 a la cantidad, es igual a: {prices['after']}")

    if not (float(prices['before'][1:])*2) == float(prices['after'][1:]):
        raise Exception("Error, el precio total nuevo deberia ser el doble")

    time.sleep(2 * x)


def test_2(driver, x):
    update_values(driver)

    print("Intentando eliminar el producto del carrito...")
    number_box = product.find_element(By.TAG_NAME, "input")
    number_box.clear()
    number_box.send_keys("0")
    apply.click()
    time.sleep(1 * x)

    driver.find_element(By.CSS_SELECTOR, "button[class='u-dialog-close-button u-icon u-text-grey-40 u-icon-2']")
    time.sleep(1 * x)

    print(
        f"La cantidad de productos en el carrito debería ser 0. Actualmente es igual a {len(product_list.find_elements(By.CSS_SELECTOR, ':scope > *'))}")

    if not len(product_list.find_elements(By.CSS_SELECTOR, ':scope > *')) == 0:
        raise Exception("El numero de articulos deberia ser igual a 0")

def test_3(driver, x):
    print("Agregando un producto...")
    add_product(driver, False, x)

    update_values(driver)
    time.sleep(1 * x)

    number_box = product.find_element(By.TAG_NAME, "input")
    number_box.clear()
    number_box.send_keys(str(stock))

    print(f"La cantidad fue asignada al maximo: {stock}")

    apply = driver.find_element(By.CSS_SELECTOR,
                                "a[class='u-align-center-xs u-btn u-button-style u-custom-color-2 u-btn-1']")
    apply.click()
    time.sleep(1 * x)

    print("Modificando el stock disponible...")
    sql = False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE productos SET stock_disponible = %s WHERE id = %s", (stock - 1, product_id))
        conn.commit()
        time.sleep(3*x)
        sql = True
        print(f"Ahora el stock es igual a {stock - 1}")
    except Exception as e:
        print("Hubo un problema con la conexion a la base de datos.")
        print(e)

    time.sleep(1 * x)
    apply.click()
    time.sleep(2 * x)

    print("Detectando si detecto que no habia stock suficiente...")
    try:
        driver.find_element(By.CSS_SELECTOR,
                            "button[class='u-dialog-close-button u-icon u-text-grey-40 u-icon-2']").click()
        print("Funciona, detecto que no habia stock suficiente.")
    except Exception as e:
        raise Exception("Error, no detecto que no habia stock suficiente.")

    time.sleep(1 * x)

    if sql:
        cursor.execute(f"UPDATE productos SET stock_disponible = %s WHERE id = %s", (stock, product_id))
        conn.commit()
        conn.close()


def test_4(driver, x):
    update_values(driver)

    print("Asignando un valor a la cantidad mayor al stock...")
    number_box = product.find_element(By.TAG_NAME, "input")
    number_box.clear()
    number_box.send_keys(str(stock + 1))
    time.sleep(1 * x)

    apply = driver.find_element(By.CSS_SELECTOR,
                                "a[class='u-align-center-xs u-btn u-button-style u-custom-color-2 u-btn-1']")
    apply.click()
    time.sleep(1 * x)

    try:
        driver.find_element(By.CSS_SELECTOR,
                            "button[class='u-dialog-close-button u-icon u-text-grey-40 u-icon-2']").click()
        print("Funciona, detecto que no habia stock suficiente")
    except NoSuchElementException:
        print("No funciona, no detecto que no habia stock suficiente")

    update_values(driver)

    print(
        f"La cantidad maxima (Stock) es igual a {stock}, la cantidad se ajusto a {product.find_element(By.TAG_NAME, 'input').get_attribute('value')}")

    if not stock == int(product.find_element(By.TAG_NAME, 'input').get_attribute('value')):
        raise Exception("Error, no ajusto el valor al stock maximo.")

def test_5(driver, x):
    prices["before"] = driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")[2].text

    code_box = driver.find_element(By.ID, "codigo")
    code_box.send_keys("Codigo Invalido")
    time.sleep(1 * x)

    driver.find_element(By.CSS_SELECTOR,
                        "a[class='u-align-center-xs u-align-right-lg u-align-right-md u-align-right-sm u-align-right-xl u-btn u-button-style u-custom-color-2 u-hover-palette-1-dark-1 u-btn-2']").click()
    time.sleep(1 * x)

    prices["after"] = driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")[2].text

    print(f"Despues de aplicar un cupon invalido, el total cambio de {prices['before'][6:]} a {prices['after'][6:]}")

    if not prices['before'][6:] == prices['after'][6:]:
        raise Exception("Error, el valor cambio, aun cuando el cupon era invalido.")


def test_6(driver, x):
    print("Modificando el stock disponible...")
    sql = False
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"UPDATE productos SET stock_disponible = %s WHERE id = %s", (0, product_id))
        conn.commit()
        print(f"El valor se ajusto a 0")
        time.sleep(3*x)
        sql = True
    except Exception as e:
        print("Hubo un problema con la conexion a la base de datos.")
        print(e)
    # print("Hubo un problema con la conexion a la base de datos.")
    time.sleep(1 * x)
    apply = driver.find_element(By.CSS_SELECTOR,
                                "a[class='u-align-center-xs u-btn u-button-style u-custom-color-2 u-btn-1']")
    apply.click()
    time.sleep(1 * x)

    try:
        driver.find_element(By.CSS_SELECTOR,
                            "button[class='u-dialog-close-button u-icon u-text-grey-40 u-icon-2']").click()
        print("Funciona, detecto que no habia stock suficiente")
    except Exception as e:
        print("No funciona, no detecto que no habia stock suficiente")

    time.sleep(1 * x)
    update_values(driver, True)
    time.sleep(1 * x)
    print(
        f"La cantidad de productos deberia ser igual a 0, ahora mismo es igual a {len(product_list.find_elements(By.CSS_SELECTOR, ':scope > *'))}")

    if not len(product_list.find_elements(By.CSS_SELECTOR, ':scope > *')) == 0:
        raise Exception("Error, la cantidad de productos no es igual a 0.")

    if sql:
        cursor.execute(f"UPDATE productos SET stock_disponible = %s WHERE id = %s", (stock, product_id))
        conn.commit()
        conn.close()
        print("Poniendo otro producto en el carrito...")
        add_product(driver, False, x)


def test_7(driver, x):
    prices["before"] = driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")[2].text[6:]

    driver.find_element(By.CSS_SELECTOR,
                        "a[class='u-align-center-xs u-align-right-lg u-align-right-md u-align-right-sm u-align-right-xl u-btn u-button-style u-custom-color-2 u-hover-palette-1-dark-1 u-btn-3']").click()
    time.sleep(6 * x)

    prices["after"] = driver.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")[2].text[6:]

    print(f"El total deberia ser {prices['before']}, en el CheckOut se representa como {prices['after']}")

    if not prices['before'] == prices['after']:
        raise Exception("Error, el total no es igual en el CheckOut y en el carrito")

    time.sleep(5 * x)


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--window-size=1920,1080")

x = 6
driver = webdriver.Chrome(options=options)
driver.get(urlPagina)
time.sleep(3 * x)

# Se probará la funcion del carrito
# Esta parte de la página sirve para las siguientes funciones:

# 1. Modificar cantidades de los productos del carrito
# Para esto utiliza un input donde se cambia la cantidad del producto, y luego se utiliza un boton para aplicar
# los cambios

# 2. Eliminar productos del carrito
# Se hace lo mismo del anterior, pero en este caso la cantidad debe ser 0, por lo que cuando se aplique el cambio,
# el producto debe desaparecer del carrito

# 3. Modificar las cantidades de los productos del carrito automaticamente dependiendo del stock
# Cuando abres el carrito y la cantidad de un producto en el carrito es mayor al stock disponible, este se
# actualizara para poner el maximo disponible, junto con un mensaje avisandote del cambio

# 4. No dejarte modificar la cantidad de un producto en carrito si es mayor a su stock
# Al igual que el anterior, pero este se muestra cuando presionas el boton de aplicar cambio

# 5. Añadir cupones y aplicarlos
# Tiene un recuadro en el cual se ingresa el cupon y un boton en donde se aplica. Ahora mismo no hay cupones
# disponibles, asi que solo se comprobara que no haga ningun cambio

# 6. Eliminar productos que no tienen stock automaticamente
# Cuando apliques un cambio o actualices la página, automaticamente eliminará productos con stock de 0

# 7. Llevar a la página de CheckOut con el mismo total que se presentó en el carrito

print("Agregando un producto...")

add_product(driver, True, x)

print("\nPrueba #1\n")  # Probando la funcion 1

test_1(driver, x)

print("\nPrueba #2\n")  # Probando la funcion 2

test_2(driver, x)

print("\nPrueba #3\n")  # Probando la funcion 3

test_3(driver, x)

print("\nPrueba #4\n")  # Probando la funcion 4

test_4(driver, x)

print("\nPrueba #5\n")  # Probando la funcion 5

test_5(driver, x)

print("\nPrueba #6\n")  # Probando la funcion 6

test_6(driver, x)

print("\nPrueba #7\n")  # Probando la funcion 7

test_7(driver, x)

driver.quit()  # Cerrar el navegador
