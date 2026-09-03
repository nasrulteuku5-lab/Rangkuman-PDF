import streamlit as st
import google.generativeai as genai
from weasyprint import HTML
import tempfile
import os

st.set_page_config(page_title="Rangkuman Percakapan ke PDF", layout="centered")

st.title("🤖 Pembuat Rangkuman Percakapan ke PDF")
st.write(
    "Tempel teks percakapanmu di bawah ini, AI akan merangkumnya dan menghasilkan"
    " file PDF siap unduh."
)

api_key = st.text_input("Masukkan Gemini API Key:", type="password")

chat_text = st.text_area(
    "Tempel teks percakapan di sini:",
    height=200,
    placeholder="Contoh: User: Halo... AI: Halo ada yang bisa dibantu?...",
)

if st.button("Buat Rangkuman & PDF"):
  if not api_key:
    st.error("Mohon masukkan Gemini API Key terlebih dahulu.")
  elif not chat_text:
    st.error("Mohon masukkan teks percakapan yang ingin dirangkum.")
  else:
    with st.spinner("Sedang memproses rangkuman dengan AI..."):
      try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = f"""
                Bertindaklah sebagai Asisten Profesional. Analisis teks percakapan berikut, lalu buatkan rangkuman yang terstruktur rapi dalam format HTML (gunakan tag <h2>, <p>, <ul>, <li>). 
                Struktur rangkuman harus mencakup:
                1. Topik Utama Pembahasan
                2. Poin-Poin Penting / Keputusan
                3. Kesimpulan atau Tindak Lanjut

                Teks Percakapan:
                {chat_text}
                """

        response = model.generate_content(prompt)
        html_content = response.text

        if "```html" in html_content:
          html_content = (
              html_content.split("```html")[1].split("```")[0].strip()
          )
        elif "```" in html_content:
          html_content = html_content.split("```")[1].split("```")[0].strip()

        styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; color: #333; }}
                    h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
                    ul {{ margin-bottom: 20px; }}
                    li {{ margin-bottom: 8px; }}
                </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".pdf"
        ) as tmp_file:
          pdf_path = tmp_file.name

        HTML(string=styled_html).write_pdf(pdf_path)

        st.success("Rangkuman PDF berhasil dibuat!")

        with open(pdf_path, "rb") as pdf_file:
          st.download_button(
              label="📥 Unduh File PDF",
              data=pdf_file,
              file_name="rangkuman_percakapan.pdf",
              mime="application/pdf",
          )

      except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
