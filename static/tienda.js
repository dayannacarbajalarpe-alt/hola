// tienda.js

const productos = productosDB;  // viene inyectado desde Flask

function render() {
  const seleccionadas = Array.from(
    document.querySelectorAll('input[name="categoria"]:checked')
  ).map(c => c.value);

  let lista = productos.filter(p =>
    seleccionadas.length === 0 || seleccionadas.includes(p.categoria)
  );

  const orden = document.getElementById('orden').value;
  if (orden === 'asc') lista.sort((a, b) => a.precio - b.precio);
  if (orden === 'desc') lista.sort((a, b) => b.precio - a.precio);

  const grid = document.getElementById('grid');
  grid.innerHTML = lista.map(p => `
  <div class="producto">
    <div class="producto-img">
      <img src="/static/img/${p.imagen}" style="width:100%; height:100%; object-fit:cover;">
    </div>
    <p class="producto-nombre">${p.nombre}</p>
    <p class="producto-precio">S/ ${p.precio.toFixed(2)}</p>
    <a href="/detalles/${p.id}" class="btn-detalles">Ver detalles</a>
  </div>
`).join('');

  if (lista.length === 0) {
    grid.innerHTML = '<p>No hay productos con estos filtros</p>';
  }
}

// Escuchar cambios en checkboxes y select
document.querySelectorAll('input[name="categoria"]').forEach(c =>
  c.addEventListener('change', render)
);
document.getElementById('orden').addEventListener('change', render);

// Mostrar productos al cargar la página
render();
