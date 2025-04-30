
document.addEventListener("DOMContentLoaded", () => {
  let cart = JSON.parse(localStorage.getItem('cart')) || [];
  let productDetails = [];

  // Actualizar el contador del carrito
  function updateCartCounter() {
    const cartCounter = document.getElementById('cart-counter');
    const itemCount = cart.reduce((total, item) => total + item.quantity, 0);

    if (itemCount === 0) {
      document.getElementById("TextoModal").textContent = `Your cart is empty`;
      document.getElementById("invisible").click();
    }
    cartCounter.innerHTML = itemCount > 9 ? '9+' : itemCount + "&nbsp;";
  }

  // Función para consultar la API y obtener los detalles completos de los productos
  async function fetchProductDetails(cartItems) {
    const apiURL = "https://don-baraton-api-f9bu.vercel.app/get_products"; // Cambia a la URL de tu API
    const response = await fetch(apiURL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ products: cartItems })
    });
    if (response.ok) {
      return await response.json();
    } else {
      console.error("Error al obtener los detalles de los productos.");
      return [];
    }
  }

  // Función para actualizar el carrito
  async function updateCart() {
    const cartItems = document.querySelectorAll('#elementosCarrito input[type="number"]');
    // Recorrer el carrito en orden inverso
    cartItems.forEach((input, i) => {
      const newQuantity = parseInt(input.value);
      const productId = productDetails[i].id;

      // Buscar el índice del producto en el carrito
      const cartIndex = cart.findIndex(item => parseInt(item.id) === productId);

      if (cartIndex !== -1) {
        if (newQuantity === 0) {
          // Eliminar el artículo del carrito si la cantidad es 0
          cart.splice(cartIndex, 1);
        } else {
          // Actualizar solo la cantidad sin modificar los otros datos
          cart[cartIndex].quantity = newQuantity;
          input.value = newQuantity;
        }
      }
    });

    // Guardar solo la cantidad actualizada en localStorage
    localStorage.setItem('cart', JSON.stringify(cart));


    //console.log("cart");
    //console.log(cart);

    // Consultar la API solo si aún no se ha hecho
    if (productDetails.length !== 0) {
      productDetails = await fetchProductDetails(cart.map(item => ({ id: item.id, quantity: item.quantity })));
    }

    //console.log("productDetails");
    //console.log(productDetails);


    // Volver a renderizar el carrito con los datos actualizados
    renderCartItems(productDetails);

    // Recalcular y actualizar el total del carrito con los datos actualizados
    updateCartTotal(productDetails);

    // Actualizar el contador del carrito
    updateCartCounter();
  }

  // Función para recalcular el total del carrito usando los datos actualizados de la API
  function updateCartTotal(products) {
    const cartTotalElement = document.querySelector('.u-custom-html-5 table tbody tr:last-child td:last-child');
    const cartSubtotalElement = document.querySelector('.u-custom-html-5 table tbody tr:first-child td:last-child');
    const cartIvaElement = document.querySelector('.u-custom-html-5 table tbody tr:nth-child(2) td:last-child');

    const total = products.reduce((total, item) => total + (item.precio_despues_descuento * item.quantity), 0);
    const iva = (total * 0.16).toFixed(2);  // 16% de IVA
    const subtotal = (total - iva).toFixed(2);  // Subtotal = Total - IVA

    // Actualiza los valores de la tabla
    cartSubtotalElement.textContent = `$${subtotal}`;
    cartIvaElement.textContent = `$${iva}`;
    cartTotalElement.textContent = `$${total.toFixed(2)}`;
  }

  // Función para renderizar los productos en el carrito
  function renderCartItems(products) {
    const cartContainer = document.querySelector('#elementosCarrito');
    cartContainer.innerHTML = ''; // Limpiamos el contenido actual
    products.forEach((product, index) => {
      if (product.stock_disponible === 0) {

        const cartIndex = cart.findIndex(item => parseInt(item.id) === product.id);
        console.log("cartIndex");
        console.log(cartIndex);


        if (cartIndex !== -1) {
          cart.splice(cartIndex, 1);
        }

        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartCounter();

        // Hacer que cambie el mensaje en la ventana modal
        document.getElementById("TextoModal").textContent = `One item is out of stock`;
        document.getElementById("invisible").click();

        return;

      } else if (product.quantity > product.stock_disponible) {
        product.quantity = product.stock_disponible;
        const cartIndex = cart.findIndex(item => parseInt(item.id) === product.id);
        cart[cartIndex].quantity = product.stock_disponible;
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartCounter();
        document.getElementById("TextoModal").textContent = `Limited stock for one item`;
        document.getElementById("invisible").click();
      }

      const totalPrice = (product.precio_despues_descuento * product.quantity).toFixed(2);
      const productHTML = `
                    <div class="data-layout-selected u-clearfix u-expanded-width-lg u-expanded-width-md u-expanded-width-xl u-layout-custom-sm u-layout-custom-xs u-layout-wrap u-palette-1-light-3 u-layout-wrap-4">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-container-style u-layout-cell u-shape-rectangle u-size-27-lg u-size-27-xl u-size-29-md u-size-30-sm u-size-30-xs u-layout-cell-13" data-href="./artic.html?$codigo=${product.id}">
                <div class="u-border-2 u-border-grey-25 u-container-layout u-container-layout-13">
                  <p class="u-align-left u-text u-text-default u-text-11">${product.nombre}</p>
                  <img class="u-image u-image-default u-preserve-proportions u-image-3" src="${product.link_imagen1}" alt="${product.nombre}" data-image-width="200" data-image-height="200">
                </div>
              </div>
              <div class="u-container-style u-layout-cell u-size-9 u-layout-cell-14">
                <div class="u-border-2 u-border-grey-25 u-container-layout u-container-layout-14">
                  <p class="u-align-center u-text u-text-default u-text-12">$${product.precio_despues_descuento}</p>
                </div>
              </div>
              <div class="u-container-style u-layout-cell u-size-10-lg u-size-10-xl u-size-9-md u-size-9-sm u-size-9-xs u-layout-cell-15">
                <div class="u-border-2 u-border-grey-25 u-container-layout u-container-layout-15">
                  <div class="letraPeque u-clearfix u-custom-html u-expanded-width u-custom-html-3">
                    <input type="number" min="0" style="width: 100%; padding: 10px;" value="${product.quantity}">
                  </div>
                </div>
              </div>
              <div class="u-container-style u-palette-1-light-3 u-size-12-sm u-size-12-xs u-size-13-md u-size-14-lg u-size-14-xl u-layout-cell-16">
                <div class="u-border-2 u-border-grey-25 u-container-layout u-container-layout-16">
                  <p class="u-align-center u-text u-text-default u-text-13">$${totalPrice}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
            `;
      cartContainer.insertAdjacentHTML('beforeend', productHTML);
    });
  }

  // Añadir evento al botón "UPDATE CART"
  const updateCartButton = document.querySelector('.u-btn-1');
  updateCartButton.addEventListener('click', (e) => {
    e.preventDefault();

    updateCart();
  });

  // Llamar a la función de actualización del contador al cargar la página
  updateCartCounter();

  // Consultar la API para obtener los detalles de los productos al cargar la página
  fetchProductDetails(cart.map(item => ({ id: item.id, quantity: item.quantity })))
    .then(products => {
      productDetails = products;
      renderCartItems(products);
      updateCartTotal(products);  // Actualiza el Subtotal, IVA y Total con los precios de la API
    });
});



document.addEventListener("DOMContentLoaded", () => {
  // Seleccionar el botón "Proceed to checkout"
  document.querySelector('.u-btn-3').addEventListener('click', (e) => {
    e.preventDefault();

    // Obtener los productos del carrito desde el localStorage o donde lo tengas guardado
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    // Guardar el carrito en localStorage antes de proceder al checkout
    localStorage.setItem('cart', JSON.stringify(cart));

    // Redirigir a la página de checkout
    window.location.href = 'checkout.html';
  });
});

// Seleccionamos el botón de "Apply Code" y el input del código
const applyButton = document.querySelector('.u-btn-2');
const codigoInput = document.getElementById('codigo');

applyButton.addEventListener('click', (e) => {
  e.preventDefault(); // Evita la acción por defecto del enlace

  // Verificar si el input está vacío
  if (codigoInput.value.trim() === "") {
    mostrarErrorEnInput("Falta escribir un código de descuento");
  } else {
    mostrarErrorEnInput("El código es incorrecto");
  }
});

// Función para mostrar el error en el input
function mostrarErrorEnInput(mensaje) {
  codigoInput.style.border = "2px solid red";
  codigoInput.style.color = "red";
  codigoInput.value = ""; // Limpiar el contenido del input
  codigoInput.placeholder = mensaje; // Mostrar el mensaje de error como placeholder

  // Evento para borrar el mensaje al hacer click o presionar una tecla
  codigoInput.addEventListener('focus', limpiarError); // Al hacer click
  codigoInput.addEventListener('keydown', limpiarError); // Al escribir
}

// Función para limpiar el error cuando el usuario interactúa con el input
function limpiarError() {
  codigoInput.style.border = ""; // Restaurar el borde
  codigoInput.style.color = ""; // Restaurar el color del texto
  codigoInput.placeholder = "Code"; // Restaurar el placeholder original
  codigoInput.removeEventListener('focus', limpiarError); // Remover los eventos después de limpiar
  codigoInput.removeEventListener('keydown', limpiarError);
}



function eliminarDiacriticosEs(texto) {
  return texto
         .normalize('NFD')
         .replace(/([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+/gi,"$1")
         .normalize();
}

document.getElementById('Buscar').addEventListener('submit', function (event) {
  event.preventDefault(); // Prevent the default form submission
  var query = document.querySelector('#Buscar input[name="search"]').value;
  query = eliminarDiacriticosEs(query);
  if (query) {
    window.location.href = "./product_list.html?" + encodeURIComponent(query.trim().replace(/\s+/g, '-'));
  }
});

