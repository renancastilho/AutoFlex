const api = {
    produtos: '/produtos',
    materias: '/materias-primas',
    associacoes: '/associacoes',
    producao: '/producao/sugerida'
}

const formato_brl = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
function parse_decimal_pt(valor_str) {
    if (typeof valor_str !== 'string') return NaN
    const limpo = valor_str.replace(/\s/g, '').replace(',', '.')
    const num = parseFloat(limpo)
    if (isNaN(num)) return NaN
    return Math.round(num * 100) / 100
}

async function carregar_produtos() {
    const r = await fetch(api.produtos)
    const itens = await r.json()
    const lista = document.getElementById('lista-produtos')
    const select = document.getElementById('produto-selecionado')
    lista.innerHTML = ''
    select.innerHTML = ''
    itens.forEach(p => {
        const div = document.createElement('div')
        div.className = 'item'
        div.innerHTML = `<div><b>${p.codigo}</b> ${p.nome} - ${formato_brl.format(p.valor)}</div>
      <div>
        <button class="secondary" data-id="${p.id}" data-acao="editar">Editar</button>
        <button data-id="${p.id}" data-acao="excluir">Excluir</button>
      </div>`
        lista.appendChild(div)
        const opt = document.createElement('option')
        opt.value = p.id
        opt.textContent = `${p.codigo} - ${p.nome}`
        select.appendChild(opt)
    })
}

async function carregar_materias() {
    const r = await fetch(api.materias)
    const itens = await r.json()
    const lista = document.getElementById('lista-materias')
    const select = document.getElementById('materia-selecionada')
    lista.innerHTML = ''
    select.innerHTML = ''
    itens.forEach(m => {
        const div = document.createElement('div')
        div.className = 'item'
        const qtd = Number(m.quantidade_estoque)
        div.innerHTML = `<div><b>${m.codigo}</b> ${m.nome} - estoque: ${qtd.toFixed(2)} ${m.unidade_medida}</div>
      <div>
        <button class="secondary" data-id="${m.id}" data-acao="editar">Editar</button>
        <button data-id="${m.id}" data-acao="excluir">Excluir</button>
      </div>`
        lista.appendChild(div)
        const opt = document.createElement('option')
        opt.value = m.id
        opt.textContent = `${m.codigo} - ${m.nome}`
        select.appendChild(opt)
    })
}

async function carregar_ingredientes() {
    const produto_id = document.getElementById('produto-selecionado').value
    if (!produto_id) return
    const r = await fetch(`${api.associacoes}/produto/${produto_id}`)
    const itens = await r.json()
    const lista = document.getElementById('lista-ingredientes')
    lista.innerHTML = ''
    itens.forEach(a => {
        const div = document.createElement('div')
        div.className = 'item'
        const qtd = Number(a.quantidade_necessaria)
        div.innerHTML = `<div>#${a.id} - Matéria ${a.materia_prima_id} precisa ${qtd.toFixed(2)} ${a.unidade_medida}</div>
      <div>
        <button class="secondary" data-id="${a.id}" data-acao="editar-ingrediente">Editar</button>
        <button data-id="${a.id}" data-acao="excluir-ingrediente">Excluir</button>
      </div>`
        lista.appendChild(div)
    })
}

async function salvar_produto(e) {
    e.preventDefault()
    const codigo = document.getElementById('produto-codigo').value.trim()
    const nome = document.getElementById('produto-nome').value.trim()
    const valor = parse_decimal_pt(document.getElementById('produto-valor').value)
    if (!codigo || !nome || !valor) return
    await fetch(api.produtos, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codigo, nome, valor })
    })
    e.target.reset()
    carregar_produtos()
}

async function salvar_materia(e) {
    e.preventDefault()
    const codigo = document.getElementById('materia-codigo').value.trim()
    const nome = document.getElementById('materia-nome').value.trim()
    const quantidade_estoque = parse_decimal_pt(document.getElementById('materia-estoque').value)
    const unidade_medida = document.getElementById('materia-unidade').value
    if (!codigo || !nome || isNaN(quantidade_estoque)) return
    await fetch(api.materias, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codigo, nome, quantidade_estoque, unidade_medida })
    })
    e.target.reset()
    carregar_materias()
}

async function adicionar_ingrediente() {
    const produto_id = document.getElementById('produto-selecionado').value
    const materia_prima_id = parseInt(document.getElementById('materia-selecionada').value)
    const quantidade_necessaria = parse_decimal_pt(document.getElementById('quantidade-necessaria').value)
    const unidade_medida = document.getElementById('ingrediente-unidade').value
    if (!produto_id || !materia_prima_id || isNaN(quantidade_necessaria)) return
    await fetch(`${api.associacoes}/produto/${produto_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ materia_prima_id, quantidade_necessaria, unidade_medida })
    })
    document.getElementById('quantidade-necessaria').value = ''
    carregar_ingredientes()
}

async function editar_excluir_lista(e) {
    const botao = e.target.closest('button')
    if (!botao) return
    const acao = botao.dataset.acao
    const id = botao.dataset.id
    if (acao === 'excluir') {
        await fetch(`${api.produtos}/${id}`, { method: 'DELETE' })
        carregar_produtos()
        carregar_ingredientes()
    } else if (acao === 'editar') {
        const nome = prompt('Novo nome:')
        const valor = prompt('Novo valor (use vírgula para centavos):')
        if (!nome && !valor) return
        const body = {}
        if (nome) body.nome = nome
        if (valor) body.valor = parse_decimal_pt(valor)
        await fetch(`${api.produtos}/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
        carregar_produtos()
    }
    if (acao === 'excluir-ingrediente') {
        await fetch(`${api.associacoes}/${id}`, { method: 'DELETE' })
        carregar_ingredientes()
    } else if (acao === 'editar-ingrediente') {
        const quantidade_necessaria = prompt('Nova quantidade necessária (use vírgula para centavos):')
        const unidade_medida = prompt('Nova unidade (kg, g, un):')
        if (!quantidade_necessaria && !unidade_medida) return
        const body = {}
        if (quantidade_necessaria) body.quantidade_necessaria = parse_decimal_pt(quantidade_necessaria)
        if (unidade_medida) body.unidade_medida = unidade_medida
        await fetch(`${api.associacoes}/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
        carregar_ingredientes()
    }
}

async function editar_excluir_materias(e) {
    const botao = e.target.closest('button')
    if (!botao) return
    const acao = botao.dataset.acao
    const id = botao.dataset.id
    if (acao === 'excluir') {
        await fetch(`${api.materias}/${id}`, { method: 'DELETE' })
        carregar_materias()
        carregar_ingredientes()
    } else if (acao === 'editar') {
        const nome = prompt('Novo nome:')
        const quantidade_estoque = prompt('Nova quantidade (use vírgula para centavos):')
        const unidade_medida = prompt('Nova unidade (kg, g, un):')
        if (!nome && !quantidade_estoque) return
        const body = {}
        if (nome) body.nome = nome
        if (quantidade_estoque) body.quantidade_estoque = parse_decimal_pt(quantidade_estoque)
        if (unidade_medida) body.unidade_medida = unidade_medida
        await fetch(`${api.materias}/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
        carregar_materias()
    }
}

async function calcular_producao() {
    const r = await fetch(api.producao)
    const dados = await r.json()
    const lista = document.getElementById('lista-producao')
    const total = document.getElementById('valor-total')
    lista.innerHTML = ''
    dados.itens.forEach(i => {
        const div = document.createElement('div')
        div.className = 'item'
        div.innerHTML = `<div><b>${i.codigo}</b> ${i.nome} → ${i.quantidade} un</div><div>${formato_brl.format(i.valor_total_item)}</div>`
        lista.appendChild(div)
    })
    total.textContent = `Valor total: ${formato_brl.format(dados.valor_total)}`
    carregar_materias()
}

document.getElementById('form-produto').addEventListener('submit', salvar_produto)
document.getElementById('form-materia').addEventListener('submit', salvar_materia)
document.getElementById('btn-adicionar-ingrediente').addEventListener('click', adicionar_ingrediente)
document.getElementById('btn-calcular').addEventListener('click', calcular_producao)
document.getElementById('lista-produtos').addEventListener('click', editar_excluir_lista)
document.getElementById('lista-materias').addEventListener('click', editar_excluir_materias)
document.getElementById('produto-selecionado').addEventListener('change', carregar_ingredientes)

carregar_produtos().then(carregar_materias).then(carregar_ingredientes)
