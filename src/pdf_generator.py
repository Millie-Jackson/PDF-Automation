"""
src/pdf_generator.py
"""


from fpdf import FPDF
from datetime import datetime


# Brand Colours
BRAND_PURPLE = (42, 0, 78)  # 2a004e
BRAND_TEAL =   (3, 76,83)   # 034c52
BRAND_BLUE =   (3, 52, 110) # 03346e
ZEBRA_GRAY =   (245, 245, 245)


class ProductSheetPDF(FPDF):

    def __init__(self):
        super(). __init__()
        self.set_auto_page_break(auto=True, margin=15)

        self.add_font("Lexend", "", "templates/fonts/Lexend-Regular.ttf", uni=True)
        self.add_font("Lexend", "B", "templates/fonts/Lexend-Bold.ttf", uni=True)
        self.set_font("Lexend", "", 12)


    def cover_page(self, title="Product Sheet"):

        self.add_page()
        self.set_fill_color(240, 240, 255)
        self.rect(0, 0, self.w, self.h, style='F')
        self.image("templates/logo.png", x=10, y=8, w=20)
        self.set_text_color(*BRAND_PURPLE)
        self.set_font("Lexend", "B", 28)
        self.set_y(110)
        self.cell(0, 20, title, align="C", ln=True)
    
    def header(self):

        if self.page_no() == 1:
            return
        
        self.set_font("Lexend", "B", 16)
        self.set_text_color(*BRAND_BLUE)
        self.cell(0, 10, "Product Sheet", ln=True, align="C")
        self.ln(15)

    def footer(self):

        if self.page_no() == 1:
            return
        
        self.set_y(-15)
        self.set_font("Lexend", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Millie Jackson | nestedloop.ai | {datetime.now().strftime('%Y-%m-%d')}", 0, 0, "C")

    def add_product_block(self, product: dict, stripe: bool = False):

        fill = stripe
        self.set_fill_color(*ZEBRA_GRAY if fill else (255, 255, 255))
        self.set_text_color(0, 0, 0)
        self.set_font("Lexend", "", 12)
        self.cell(0, 10, "", ln=True)

        y_start = self.get_y()
        self.set_x(15)

        # Name and SKU
        self.set_font("Lexend", "B", 13)
        self.set_text_color(*BRAND_TEAL)
        self.multi_cell(0, 8, f"{product['Name']} ({product['SKU']})", border=0, align='L', fill=True)
        
        # Description
        self.set_font("Lexend", "", 11)
        self.set_text_color(0, 0, 0)
        self.set_x(15)
        self.multi_cell(0, 8, product["Description"], border=0, align='L')

        # Price
        self.set_x(15)
        self.cell(0, 8, f"Price: £{product['Price']:.2f}", ln=True)
        if "PriceWithVAT" in product:
            self.set_x(15)
            self.cell(0, 8, f"Price (with VAT): £{product['PriceWithVAT']:.2f}", ln=True)

        self.set_x(15)
        self.cell(0, 8, f"In Stock: {product['Stock']}", ln=True) 

        # Border box
        y_end = self.get_y()
        self.rect(x=10, y=y_start - 2, w=190, h=(y_end - y_start + 10))  
                  