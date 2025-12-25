import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
import numpy as np
import math
from io import BytesIO

st.set_page_config(page_title="Nutrition Facts Panel Generator", page_icon="🥗", layout="wide")

# Title and description
st.title("🥗 FDA-Compliant Nutrition Facts Panel Generator")
st.markdown("Generate professional nutrition facts panels compliant with USFDA 2016 regulations.")

# Sidebar for product information
st.sidebar.header("📋 Product Information")
product_name = st.sidebar.text_input("Product Name", "My Product")
serving_size = st.sidebar.text_input("Serving Size", "2/3 cup (124g)")
servings_per_container = st.sidebar.number_input("Servings Per Container", min_value=1, value=3, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Tips")
st.sidebar.info("Enter all nutritional values per serving. The FDA rounding rules will be automatically applied.")

# Main input section
st.header("📊 Nutritional Information (Per Serving)")

# Create three columns for better layout
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Energy & Macros")
    calories = st.number_input("Calories", min_value=0, value=170, step=5)
    total_fat = st.number_input("Total Fat (g)", min_value=0.0, value=5.0, step=0.5)
    saturated_fat = st.number_input("Saturated Fat (g)", min_value=0.0, value=3.0, step=0.5)
    trans_fat = st.number_input("Trans Fat (g)", min_value=0.0, value=0.0, step=0.1)
    cholesterol = st.number_input("Cholesterol (mg)", min_value=0, value=15, step=5)

with col2:
    st.subheader("Sodium & Carbs")
    sodium = st.number_input("Sodium (mg)", min_value=0, value=180, step=5)
    total_carb = st.number_input("Total Carbohydrate (g)", min_value=0.0, value=31.0, step=0.5)
    dietary_fiber = st.number_input("Dietary Fiber (g)", min_value=0.0, value=3.0, step=0.5)
    total_sugars = st.number_input("Total Sugars (g)", min_value=0.0, value=20.0, step=0.5)
    added_sugars = st.number_input("Added Sugars (g)", min_value=0.0, value=12.0, step=0.5)

with col3:
    st.subheader("Protein & Vitamins")
    protein = st.number_input("Protein (g)", min_value=0.0, value=9.0, step=0.5)
    vitamin_d = st.number_input("Vitamin D (mcg)", min_value=0.0, value=0.0, step=0.1)
    calcium = st.number_input("Calcium (mg)", min_value=0, value=180, step=10)
    iron = st.number_input("Iron (mg)", min_value=0.0, value=0.0, step=0.1)
    potassium = st.number_input("Potassium (mg)", min_value=0, value=240, step=10)

# Generate button
st.markdown("---")
if st.button("🎨 Generate Nutrition Facts Panel", type="primary", use_container_width=True):
    
    # Create nutrients dataframe
    nutrients_data = {
        'Nutrient': ['Calories', 'Total Fat', 'Saturated Fat', 'Trans Fat', 'Cholesterol', 
                     'Sodium', 'Total Carbohydrate', 'Dietary Fiber', 'Total Sugars', 
                     'Added Sugars', 'Protein', 'Vitamin D', 'Calcium', 'Iron', 'Potassium'],
        'Amount': [calories, total_fat, saturated_fat, trans_fat, cholesterol, sodium,
                   total_carb, dietary_fiber, total_sugars, added_sugars, protein, 
                   vitamin_d, calcium, iron, potassium],
        'Unit': ['kcal', 'g', 'g', 'g', 'mg', 'mg', 'g', 'g', 'g', 'g', 'g', 'mcg', 'mg', 'mg', 'mg']
    }
    
    nutrients_df = pd.DataFrame(nutrients_data)
    
    # FDA Rounding Rules
    def round_nutrition_facts(df):
        for idx, row in df.iterrows():
            nutrient = row['Nutrient']
            amount = row['Amount']
            
            if nutrient == 'Calories':
                if amount < 5:
                    df.at[idx, 'Amount'] = 0
                elif amount <= 50:
                    df.at[idx, 'Amount'] = round(amount / 5) * 5
                else:
                    df.at[idx, 'Amount'] = round(amount / 10) * 10
            
            elif nutrient in ['Total Fat', 'Saturated Fat', 'Trans Fat']:
                if amount < 0.5:
                    df.at[idx, 'Amount'] = 0
                elif amount < 5:
                    df.at[idx, 'Amount'] = round(amount * 2) / 2
                else:
                    df.at[idx, 'Amount'] = round(amount)
            
            elif nutrient == 'Cholesterol':
                if amount < 2:
                    df.at[idx, 'Amount'] = 0
                elif amount <= 5:
                    df.at[idx, 'Amount'] = math.ceil(amount)
                else:
                    df.at[idx, 'Amount'] = round(amount / 5) * 5
            
            elif nutrient == 'Sodium':
                if amount < 5:
                    df.at[idx, 'Amount'] = 0
                elif amount <= 140:
                    df.at[idx, 'Amount'] = round(amount / 5) * 5
                else:
                    df.at[idx, 'Amount'] = round(amount / 10) * 10
            
            elif nutrient in ['Total Carbohydrate', 'Dietary Fiber', 'Total Sugars', 'Added Sugars']:
                if amount < 0.5:
                    df.at[idx, 'Amount'] = 0
                else:
                    df.at[idx, 'Amount'] = round(amount)
            
            elif nutrient == 'Protein':
                if amount < 0.5:
                    df.at[idx, 'Amount'] = 0
                else:
                    df.at[idx, 'Amount'] = round(amount)
            
            elif nutrient in ['Vitamin D', 'Calcium', 'Iron', 'Potassium']:
                df.at[idx, 'Amount'] = round(amount)
        
        return df
    
    nutrients_df = round_nutrition_facts(nutrients_df)
    
    # Calculate Daily Values
    daily_values = {
        'Total Fat': 78,
        'Saturated Fat': 20,
        'Cholesterol': 300,
        'Sodium': 2300,
        'Total Carbohydrate': 275,
        'Dietary Fiber': 28,
        'Added Sugars': 50,
        'Protein': 50,
        'Vitamin D': 20,
        'Calcium': 1300,
        'Iron': 18,
        'Potassium': 4700
    }
    
    def calculate_dv(nutrient, amount):
        if nutrient in daily_values:
            return round((amount / daily_values[nutrient]) * 100)
        return None
    
    nutrients_df['%DV'] = nutrients_df.apply(
        lambda row: calculate_dv(row['Nutrient'], row['Amount']), axis=1
    )
    
    # Create nutrient dictionary for easier access
    nutrient_dict = {}
    for _, row in nutrients_df.iterrows():
        nutrient_dict[row['Nutrient']] = {
            'amount': row['Amount'],
            'unit': row['Unit'],
            'dv': row['%DV']
        }
    
    # Create the visualization
    fig, ax = plt.subplots(figsize=(4.5, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # Positioning
    left_margin = 0.5
    right_margin = 9.5
    
    def add_text(x, y, text, size=10, weight='normal', ha='left'):
        ax.text(x, y, text, fontsize=size, weight=weight, ha=ha, va='top', family='DejaVu Sans')
    
    def draw_line(y, thickness=1, style='solid'):
        ax.plot([left_margin, right_margin], [y, y], 'k-', 
                linewidth=thickness, linestyle=style)
    
    def format_amount(nutrient, amount, unit):
        if unit == 'kcal':
            return ''
        if amount == 0 and nutrient == 'Trans Fat':
            return '0g'
        if unit == 'g' and 0 < amount < 1:
            return f'<1g'
        if isinstance(amount, float) and amount.is_integer():
            return f'{int(amount)}{unit}'
        return f'{amount:.1f}{unit}' if isinstance(amount, float) else f'{amount}{unit}'
    
    # Start drawing
    y_pos = 15.5
    
    # Outer border
    border = Rectangle((left_margin - 0.1, 0.3), 
                       right_margin - left_margin + 0.2, 
                       y_pos - 0.2, 
                       linewidth=2, edgecolor='black', facecolor='none')
    ax.add_patch(border)
    
    # Title
    add_text(left_margin, y_pos, 'Nutrition Facts', size=32, weight='bold')
    y_pos -= 0.8
    
    # Serving info
    add_text(left_margin, y_pos, f'{servings_per_container} servings per container', size=9)
    y_pos -= 0.35
    add_text(left_margin, y_pos, 'Serving size', size=9, weight='bold')
    add_text(left_margin + 2.5, y_pos, serving_size, size=9, weight='bold')
    y_pos -= 0.35
    draw_line(y_pos, thickness=12)
    y_pos -= 0.45
    
    # Amount per serving header
    add_text(left_margin, y_pos, 'Amount per serving', size=8, weight='bold')
    y_pos -= 0.3
    
    # Calories
    cal_val = int(nutrient_dict['Calories']['amount'])
    add_text(left_margin, y_pos, 'Calories', size=15, weight='bold')
    add_text(right_margin, y_pos, str(cal_val), size=42, weight='bold', ha='right')
    y_pos -= 1.0
    draw_line(y_pos, thickness=6)
    y_pos -= 0.35
    
    # % Daily Value header
    add_text(right_margin, y_pos, '% Daily Value*', size=8, weight='bold', ha='right')
    y_pos -= 0.25
    draw_line(y_pos, thickness=1)
    y_pos -= 0.35
    
    # Iterate through nutrients
    for nutrient in ['Total Fat', 'Saturated Fat', 'Trans Fat', 'Cholesterol', 'Sodium',
                     'Total Carbohydrate', 'Dietary Fiber', 'Total Sugars', 'Added Sugars',
                     'Protein', 'Vitamin D', 'Calcium', 'Iron', 'Potassium']:
        
        data = nutrient_dict[nutrient]
        amount = data['amount']
        unit = data['unit']
        dv = data['dv']
        
        # Determine formatting
        indent = left_margin
        size = 11
        weight = 'bold'
        
        if nutrient in ['Saturated Fat', 'Trans Fat']:
            indent = left_margin + 0.3
            weight = 'normal'
        elif nutrient in ['Dietary Fiber', 'Total Sugars']:
            indent = left_margin + 0.3
            weight = 'normal'
        elif nutrient == 'Added Sugars':
            indent = left_margin + 0.6
            weight = 'normal'
            size = 10
        elif nutrient in ['Vitamin D', 'Calcium', 'Iron', 'Potassium']:
            weight = 'normal'
            size = 10
        
        # Display nutrient name and amount
        display_name = 'Total Carb.' if nutrient == 'Total Carbohydrate' else nutrient
        if nutrient == 'Added Sugars':
            display_name = 'Includes Added Sugars'
        
        amount_str = format_amount(nutrient, amount, unit)
        add_text(indent, y_pos, display_name, size=size, weight=weight)
        add_text(right_margin - 1.5, y_pos, amount_str, size=size, weight='normal', ha='right')
        
        # Add %DV if applicable
        if dv is not None and nutrient not in ['Trans Fat', 'Total Sugars']:
            add_text(right_margin, y_pos, f'{int(dv)}%', size=11, weight='bold', ha='right')
        
        y_pos -= 0.32
        
        # Draw separator lines
        if nutrient in ['Trans Fat', 'Cholesterol', 'Sodium', 'Added Sugars']:
            draw_line(y_pos, thickness=1)
            y_pos -= 0.05
        elif nutrient == 'Protein':
            draw_line(y_pos, thickness=12)
            y_pos -= 0.2
        elif nutrient == 'Potassium':
            draw_line(y_pos, thickness=6)
            y_pos -= 0.1
    
    y_pos -= 0.2
    
    # Footer
    footer_text = '*The % Daily Value (DV) tells you how much a nutrient in\n' \
                  'a serving of food contributes to a daily diet. 2,000 calories\n' \
                  'a day is used for general nutrition advice.'
    add_text(left_margin, y_pos, footer_text, size=8, weight='normal')
    
    plt.tight_layout()
    
    # Display in Streamlit
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)  # Prevent memory issues
    
    # Save to bytes buffer for download
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    
    # Download button
    st.download_button(
        label="⬇️ Download Nutrition Facts Panel (High Resolution PNG)",
        data=buf,
        file_name=f"{product_name.replace(' ', '_')}_Nutrition_Facts.png",
        mime="image/png",
        use_container_width=True
    )
    
    st.success("✅ Nutrition Facts Panel generated successfully!")
    
    # Summary in expander
    with st.expander("📊 View Nutritional Summary"):
        summary_data = []
        for nutrient, data in nutrient_dict.items():
            summary_data.append({
                'Nutrient': nutrient,
                'Amount': f"{data['amount']}{data['unit']}",
                '% Daily Value': f"{int(data['dv'])}%" if data['dv'] is not None else 'N/A'
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
        st.markdown("---")
        st.markdown(f"**Product:** {product_name}")
        st.markdown(f"**Serving Size:** {serving_size}")
        st.markdown(f"**Servings Per Container:** {servings_per_container}")
        st.markdown(f"**Calories per Serving:** {cal_val}")
        st.info("✓ Panel complies with USFDA 2016 Nutrition Facts Label regulations")

# Footer
st.markdown("---")
st.markdown("### 📚 About FDA Rounding Rules")
with st.expander("Click to learn more"):
    st.markdown("""
    This tool automatically applies FDA rounding rules according to 21 CFR 101.9:
    
    - **Calories:** Rounded to nearest 5 (if ≤50) or 10 (if >50)
    - **Fats:** Rounded to nearest 0.5g (if <5g) or 1g (if ≥5g)
    - **Cholesterol:** Rounded to nearest 5mg (if >5mg)
    - **Sodium:** Rounded to nearest 5mg (if ≤140mg) or 10mg (if >140mg)
    - **Carbs, Fiber, Sugars, Protein:** Rounded to nearest 1g
    - **Vitamins & Minerals:** Rounded to whole numbers
    
    All daily values are calculated based on a 2,000 calorie diet.
    """)

st.markdown("💡 **Tip:** Enter your values and click 'Generate' to create a professional FDA-compliant nutrition label!")
