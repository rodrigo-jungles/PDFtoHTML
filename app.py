import os
import fitz  # PyMuPDF


def pdf_para_texto(pdf_path, output_txt):
    """Extrai texto do PDF em formato simples para IA"""
    doc = fitz.open(pdf_path)
    texto_completo = []

    for page in doc:
        texto_completo.append(page.get_text())

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(texto_completo))


def pdf_to_html_absolute(pdf_path, output_html):
    doc = fitz.open(pdf_path)
    html_content = [
        "<html><body style='background-color: #525659; display: flex; flex-direction: column; align-items: center; margin: 0;'>"]

    for page_num, page in enumerate(doc):
        width = page.rect.width
        height = page.rect.height

        # Cria o "canvas" da página
        html_content.append(f"""
        <div id='page-{page_num}' style='position: relative; width: {width}px; height: {height}px; 
             background-color: white; margin: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.5); overflow: hidden;'>
        """)

        # Extrai os blocos de conteúdo
        page_dict = page.get_text("dict")
        for block in page_dict["blocks"]:
            if "lines" in block:  # Se for um bloco de texto
                for line in block["lines"]:
                    for span in line["spans"]:
                        # Extrai propriedades do texto
                        text = span["text"]
                        font_size = span["size"]
                        # Converte cor para Hex
                        font_color = f"#{span['color']:06x}"
                        x, y = span["origin"]  # Coordenada base do texto

                        # Adiciona o texto na posição exata
                        # Ajustamos o top para bater com a baseline do PDF
                        style = (f"position: absolute; left: {x}px; top: {y - font_size}px; "
                                 f"font-size: {font_size}px; color: {font_color}; white-space: pre; "
                                 f"font-family: sans-serif; pointer-events: auto;")

                        html_content.append(
                            f"<span style='{style}'>{text}</span>")

            elif "image" in block:  # Se for uma imagem
                bbox = block["bbox"]  # [x0, y0, x1, y1]
                img_width = bbox[2] - bbox[0]
                img_height = bbox[3] - bbox[1]

                # Para uma versão completa, precisaríamos salvar a imagem em bytes/base64
                html_content.append(f"""
                <div style='position: absolute; left: {bbox[0]}px; top: {bbox[1]}px; 
                     width: {img_width}px; height: {img_height}px; border: 1px dashed red;'>
                     [Imagem: {img_width}x{img_height}]
                </div>
                """)

        html_content.append("</div>")

    html_content.append("</body></html>")

    with open(output_html, "w", encoding="utf-8") as f:
        f.write("\n".join(html_content))


# Execução - processa todos os PDFs da pasta curriculos
pasta = "curriculos"
if os.path.exists(pasta):
    for arquivo in os.listdir(pasta):
        if arquivo.endswith(".pdf"):
            caminho_pdf = os.path.join(pasta, arquivo)
            nome_base = arquivo.replace('.pdf', '')

            # Gera o HTML (visual)
            nome_html = f"resultado_{nome_base}.html"
            print(f"Processando: {arquivo} -> {nome_html}")
            pdf_to_html_absolute(caminho_pdf, nome_html)

            # Gera o TXT (para IA)
            nome_txt = f"texto_{nome_base}.txt"
            print(f"Extraindo texto: {arquivo} -> {nome_txt}")
            pdf_para_texto(caminho_pdf, nome_txt)

    print("\nProcessamento concluído!")
else:
    print(f"A pasta '{pasta}' não existe!")
