const API = "/api";
const $ = (id) => document.getElementById(id);
const money = (n) => "₹" + Number(n).toLocaleString("en-IN", { maximumFractionDigits: 2 });
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
let products = [], editingId = null, timer;

function toast(msg, type = "ok") {
  const t = $("toast");
  t.textContent = msg; t.className = "show " + type;
  clearTimeout(t._h); t._h = setTimeout(() => (t.className = ""), 2800);
}

async function api(path, method = "GET", body) {
  try {
    const res = await fetch(API + path, {
      method, headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed");
    return data;
  } catch (e) {
    toast(e.message === "Failed to fetch" ? "Cannot reach server. Is Flask running?" : e.message, "err");
    throw e;
  }
}

async function loadProducts() {
  const q = encodeURIComponent($("search").value.trim());
  const cat = encodeURIComponent($("filter").value);
  products = await api(`/products?q=${q}&category=${cat}`);
  render();
  loadStats(); loadCategories();
}

async function loadStats() {
  const s = await api("/stats");
  $("sProducts").textContent = s.products;
  $("sUnits").textContent = s.units;
  $("sValue").textContent = money(s.value);
  $("sLow").textContent = s.low;
}

async function loadCategories() {
  const cats = await api("/categories");
  const cur = $("filter").value;
  $("filter").innerHTML = '<option value="">All categories</option>' +
    cats.map((c) => `<option ${c === cur ? "selected" : ""}>${esc(c)}</option>`).join("");
  $("catList").innerHTML = cats.map((c) => `<option value="${esc(c)}">`).join("");
}

function render() {
  $("empty").hidden = products.length > 0;
  $("tbody").innerHTML = products.map((p) => {
    const st = p.quantity === 0 ? ["out", "Out of stock"] : p.low_stock ? ["low", "Low stock"] : ["ok", "In stock"];
    return `<tr>
      <td>#${p.id}</td><td><b>${esc(p.name)}</b></td><td>${esc(p.category)}</td>
      <td><span class="stock"><button onclick="adjust(${p.id},-1)">−</button><b>${p.quantity}</b><button onclick="adjust(${p.id},1)">+</button></span></td>
      <td>${money(p.price)}</td><td><span class="badge ${st[0]}">${st[1]}</span></td>
      <td><button class="icon" title="Edit" onclick="openEdit(${p.id})">✏️</button>
          <button class="icon del" title="Delete" onclick="remove(${p.id})">🗑️</button></td></tr>`;
  }).join("");
  const low = products.filter((p) => p.low_stock);
  $("alertBar").hidden = low.length === 0;
  $("alertBar").innerHTML = "⚠️ <b>Low-stock alert:</b> " +
    low.map((p) => `${esc(p.name)} (${p.quantity})`).join(", ");
}

async function adjust(id, change) {
  try { await api(`/products/${id}/stock`, "PATCH", { change }); loadProducts(); } catch {}
}

async function remove(id) {
  if (!confirm("Delete this product permanently?")) return;
  try { await api(`/products/${id}`, "DELETE"); toast("Product deleted"); loadProducts(); } catch {}
}

function formData(form) {
  const f = Object.fromEntries(new FormData(form));
  return { name: f.name, category: f.category, quantity: f.quantity, price: f.price };
}

$("addForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/products", "POST", formData(e.target));
    toast("Product added"); e.target.reset(); loadProducts();
  } catch {}
});

function openEdit(id) {
  const p = products.find((x) => x.id === id);
  editingId = id; $("editId").textContent = "#" + id;
  const f = $("editForm");
  f.name.value = p.name; f.category.value = p.category;
  f.quantity.value = p.quantity; f.price.value = p.price;
  $("editDlg").showModal();
}

$("editForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api(`/products/${editingId}`, "PUT", formData(e.target));
    $("editDlg").close(); toast("Product updated"); loadProducts();
  } catch {}
});
$("cancelEdit").onclick = () => $("editDlg").close();

$("search").addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(loadProducts, 250); });
$("filter").addEventListener("change", loadProducts);

loadProducts();
