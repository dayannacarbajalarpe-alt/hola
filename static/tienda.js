// tienda.js

const productos = [
  {id:1, nombre: "Jean slim azul", categoria: "jeans", precio: 89.00 },
  {id:2, nombre: "Jean recto negro", categoria: "jeans", precio: 99.00 },
  {id:3, nombre: "Zapatillas urbanas", categoria: "zapatos", precio: 159.00 },
  {id:4, nombre: "Botines cuero", categoria: "zapatos", precio: 229.00 },
  {id:5, nombre: "Polo básico blanco", categoria: "polos", precio: 39.00 },
  {id:6, nombre: "Polo oversize gris", categoria: "polos", precio: 49.00 },
  {id:7, nombre: "Casaca denim", categoria: "casacas", precio: 179.50 },
  {id:8, nombre: "Casaca bomber", categoria: "casacas", precio: 199.00 }
];

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
      <div class="producto-img"></div>
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
