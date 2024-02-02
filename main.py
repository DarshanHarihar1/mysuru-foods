from openai import OpenAI
import streamlit as st
import re
import pandas as pd
import os

# Set up your OpenAI API key
from openai import OpenAI

# Set your OpenAI API key


client = OpenAI(api_key="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")

# Global variable to store selected items
selected_items = []

user_details = []
try:
    existing_user_details = pd.read_csv('user_details.csv')
    user_details.extend(existing_user_details.to_dict(orient='records'))
except FileNotFoundError:
    pass

# Global variable to store launching soon details
launching_soon_details = []
try:
    existing_launching_soon_details = pd.read_csv('launching_soon_details.csv')
    launching_soon_details.extend(existing_launching_soon_details.to_dict(orient='records'))
except FileNotFoundError:
    pass

# Global variable to store leave a review details
leave_review_details = []
try:
    existing_leave_review_details = pd.read_csv('leave_review_details.csv')
    leave_review_details.extend(existing_leave_review_details.to_dict(orient='records'))
except FileNotFoundError:
    pass



# Function to interact with OpenAI GPT-3.5-turbo API
# Function to interact with OpenAI GPT-3.5-turbo API with a simplified prompt
def chatbot(user_input, review_option):
    # Create a prompt with a simplified instruction
    prompt = f"Generate a concise {review_option.lower()} review in 2-3 sentences based on the input: {user_input}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150 
    )

    # Read the response message content
    response_message = response.choices[0].message.content
    return response_message


# Function to display items with a timed confirmation
def display_items(items, email, number):
    global selected_items
    # Create a dictionary to store the quantity of each item
    item_quantities = {item: 0 for item in items}

    # Display items with quantity selector
    for item in items:
        quantity = st.number_input(f'{item}', min_value=0, max_value=10, key=item)
        item_quantities[item] = quantity

    # Get selected items based on quantity and calculate the total cost
    selected_items = []
    total_cost = 0

    for item, quantity in item_quantities.items():
        if quantity > 0:
            match = re.search(r'Rs(\d+)', item)
            if match:
                price = int(match.group(1))
                total_cost += price * quantity
                selected_items.append(f'{item} - {quantity}')

    st.text_area("Bot:", value="Selected items:\n" + "\n".join(selected_items))
    
    st.text_area("Bot:", value=f'Total Cost for selected items: Rs{total_cost}')
    
    confirmation_selection = st.button("Confirm Selection")
    if confirmation_selection:
        st.text_area("Bot:", value=f'Thank you for ordering with Mysuru Foods! \nOur representatives will soon contact you regarding your order on: \nEmail: {email}\nMobile No: {number}')
        
        user_details.append({'Phone Number': number, 'Email': email, 'Selected Items': selected_items, 'Total Cost': total_cost})
        df = pd.DataFrame(user_details)
        df.to_csv('user_details.csv', index=False)
        
def about_us():
    about_us_option = st.selectbox("Select an option:", ["Leave a review", "Contact us", "Launching soon"], index=None)

    if about_us_option == "Leave a review":
        leave_review()

    elif about_us_option == "Contact us":
        st.text_area("Bot:", value="You can contact us for more queries at mysurufoods@gmail.com. We will respond to you within the next two business days.")

    elif about_us_option == "Launching soon":
        launching_soon()
                
# Function to handle "Launching soon" options
def launching_soon():
    st.text_area("Bot:", value="Mysuru Foods is coming up with two more exciting services for you soon:\n"
                                "- On-ground legal/official/parental/property-related assistance in Bangalore and Mysuru for NRI's.\n"
                                "- Platform for the sale of artistic products and goods from villages and NGOs available for sale in Bengaluru and Mysuru.\n"
                                )

    interested = st.radio("Are you interested in receiving emails about our updates?", ["Yes", "No"], index=None)

    if interested == "Yes":
        user_email = st.text_input("Enter your email:")
        if user_email:
            st.text_area("Bot:", value=f"Thank you for showing interest! We will keep you updated on our upcoming services. Your email: {user_email}")
            launching_soon_details.append({'Email': user_email})
            df_launching_soon = pd.DataFrame(launching_soon_details)
            df_launching_soon.to_csv('launching_soon_details.csv', index=False)
        else:
            st.warning("Please enter a valid email address.")

                
                
# Function to handle "Leave a review" options
def leave_review():
    review_option = st.selectbox("Select a review option:", ["Review Experience", "Review Product"], index=None)

    if review_option == "Review Experience" or review_option == "Review Product":
        name_review = st.text_input('Enter Your Name')
        if name_review:
           st.text_area("Bot:", value=f"Please share a few words of your {review_option.lower()}.")

           user_review = st.text_input(f"Your {review_option.lower()} review:")

           if user_review:
               # Use OpenAI API to generate a review based on the simplified prompt
               generated_review = chatbot(user_review, review_option)

               st.text_area("Bot:", value=f"Here is your generated {review_option.lower()} review:\n{generated_review}")
               


               feedback_option = st.radio("How do you feel about the generated review?", ["Like it!", "Nah, I would prefer something else!"], index=None)

               if feedback_option == "Like it!":
                   st.text_area("Bot:", value="Thank you for liking the generated review! We will post the review on your behalf.")
                   leave_review_details.append({'Name': name_review, 'Review Type': review_option, 'Generated Review': generated_review})
                   df_leave_review = pd.DataFrame(leave_review_details)
                   df_leave_review.to_csv('leave_review_details.csv', index=False)
               else:
                   st.text_area("Bot:", value="Feel free to write your own review in the text area below.")

                   user_custom_review = st.text_area("Your own review:")

                   if user_custom_review:
                       st.text_area("Bot:", value="Thank you for writing your own review! We will post the review on your behalf.")
                   else:
                       st.warning("Please write your own review before confirming.")
                       
                       
def general_enquiries():
    enquiries_option = st.selectbox("Select an option:", ["Charges", "Delivery Time"], index=None)

    if enquiries_option == "Charges":
        st.text_area("Bot:", value="COST OF OUR SERVICES\n\n"
                                    "What you pay us will be a sum of:\n"
                                    "- Cost of items you buy from Mysuru Foods Menu.\n"
                                    "- Cost of items ordered in Pick N Drop service\n"
                                    "- A service fee depending on the time and effort spent in putting things together.\n"
                                    "COURIER CHARGES\n\n"
                                    "- To calculate approximate courier cost, visit [GarudaVega Prices](https://www.garudavega.com/prices.php)\n"
                                    "- Charges depend on the weight/volume of the package and density of items packed.\n"
                                    "- You can even choose a courier service provider of your choice and inform us.")

    elif enquiries_option == "Delivery Time":
        st.text_area("Bot:", value="TIME NEEDED FOR SERVICE\n\n"
                                    "- Post checkout from our cart, an email specifying your order details and total cost (including delivery) will reach you within two working days.\n"
                                    "- Once you reconfirm the order, lead time for delivery would be about 10 days to assemble your package plus courier transit time to your destination")

            


 
        

# Streamlit app
def main():
    email = ""
    number = ""
    
    st.markdown("<h1 style='text-align: center;'>MYSURU FOODS🥘🍲</h1>", unsafe_allow_html=True)

    # Welcome message
    st.text_area("Bot:", value="Welcome! I'm here to bring the flavours of Bengaluru and Mysuru straight to your doorstep, no matter where you are in the world. Let's explore your favourite culinary delights and local ingredients together.", height=100)

    # Display user options without a default selection
    option = st.selectbox("Select an option:", ["Buy from us", "About us", "General enquiries"], index=None)
    
    
    if option == 'About us':
      about_us()

    # If user chose "Buy from us"
    if option == "Buy from us":
        st.image('https://cm4-production-assets.s3.amazonaws.com/1703142974090-black--gold-simple-new-year-sale-instagram-post-1.jpg', caption='Advertisement', use_column_width=True)

        # Get user's response to the menu question without a default selection
        menu_response = st.radio("Would you want to check the menu once?", ["Yes", "No"], index=None)

        # Handle user's menu response
        if menu_response == "Yes":
            email = st.text_input('Enter email')
            
            if email:
                number = st.text_input('Enter phone number')
                
                if number:

                    menu_category = st.selectbox("Select a menu category:", ["Culinary Delights", "Local Ingredients"], index=None)

            # Handle user's choice in the menu category
                    if menu_category == "Culinary Delights":
                       st.image('https://cm4-production-assets.s3.amazonaws.com/1703313597889-delicious-food-menu-instagram-story.jpg', caption='Advertisement', use_column_width=True)
                       sub_category = st.selectbox("Select a sub-category:", ["Condiments", "Pickle", "Sweets"], index=None)

                # Handle user's choice in the sub-category
                       if sub_category == "Condiments":
                    
                        display_items([
                        "Nippattu - 250g - Rs150",
                        "Kodubale - 250g - Rs150",
                        "Chakkuli - 250g - Rs150",
                        "Khara Seve - 250g - Rs150",
                        "Avalakki Chivda - 250g - Rs150",
                        "Mucchore - 250g - Rs150",
                        "Tengolalu - 250g - Rs150",
                        "Pheni Sandige - 250g - Rs200",
                        "Onion Sandige - 250g - Rs200",
                        "Aralu Sandige - 250g - Rs200",
                        "Rice Happala - 250g - Rs200",
                        "Jackfruit Happala - 250g - Rs200",
                        "Congress Kadlekai - 250g - Rs100",
                        "Bonda Kadlekai - 250g - Rs100",
                        "Shankara Poli - Spicy - 250g - Rs100",
                        "Shankara Poli - Sweet - 250g - Rs100",
                        "Mixed and Sweet Arecanut (Kalasida Adike) - 250g - Rs500"
                        ], email, number)

                       elif sub_category == "Pickle":
                    
                         display_items([
                        "Mango Pickle - 500g - Rs400",
                        "Lemon Pickle - 500g - Rs400",
                        "Gooseberry Pickle - 500g - Rs400",
                        "Mixed Pickle - 500g - Rs400",
                        "Heralekayi Uppinakayi - 500g - Rs400",
                        "Makaliberu Uppinakayi - 500g - Rs400"
                         ], email, number)

                       elif sub_category == "Sweets":
                    
                        display_items([
                        "Basin Laddu - 6pc - Rs200",
                        "Wheat Flour Laddu - 6pc - Rs200",
                        "Chigali Thambittu - 6pc - Rs200",
                        "Rave Unde - 6pc - Rs200",
                        "Puri Unde - 6pc - Rs150",
                        "Holige (Dates) - 6pc - Rs150",
                        "Holige (Sugar) - 6pc - Rs120",
                        "Bhadusha - 12pc - Rs240",
                        "Pheni - 6pc - Rs300",
                        "Chiroti - 6pc - Rs300"
                         ], email, number)

                    elif menu_category == "Local Ingredients":
                
                      sub_category = st.selectbox("Select a sub-category:", ["Masala", "Ready to eat", "Raw Spices", "Pooja Items"], index=None)

                # Handle user's choice in the local ingredients sub-category
                      if sub_category == "Masala":
                
                        display_items([
                        "Peanut Chatni Pudi - 500g - Rs300",
                        "Flaxseed Chatni Pudi - 500g - Rs300",
                        "Hurugadle Chatni Pudi - 500g - Rs300",
                        "Chatni Powder - 500g - Rs300",
                        "Sambar Powder - 500g - Rs300",
                        "Rasam Powder - 500g - Rs300",
                        "Puliyogare Pudi - 500g - Rs300",
                        "Gojjina Pudi - 500g - Rs300",
                        "Ragi Huri Hittu - 500g - Rs300",
                        "Menthyada Hittu - 500g - Rs300"
                        ], email, number)

                      elif sub_category == "Ready to eat":
                    
                        display_items([
                        "Uppittu - 500g - Rs250",
                        "Gojju Avalakki - 500g - Rs250",
                        "Navane Pongal - 500g - Rs250"
                        ], email, number)

                      elif sub_category == "Raw Spices":
                    
                        display_items([
                        "Dried Ginger (Natural) - 250g - Rs300",
                        "Asafoetida (Natural) - 250g - Rs500",
                        "Nutmeg (Natural) - 250g - Rs300",
                        "Palav Leaf (Natural) - 250g - Rs200",
                        "Cumin Powder - 250g - Rs400",
                        "Cumin Seeds - 250g - Rs250",
                        "Coriander Powder - 250g - Rs300",
                        "Coriander Seeds - 250g - Rs250",
                        "Cinnamon Powder - 250g - Rs250",
                        "Cinnamon (Natural) - 250g - Rs250",
                        "Pepper Powder - 250g - Rs150",
                        "Pepper Corns - 250g - Rs100",
                        "Cloves (Natural) - 250g - Rs250",
                        "Cardamom (Natural) - 250g - Rs100"
                        ], email, number)

                      elif sub_category == "Pooja Items":
                    
                        display_items([
                        "Hoobatti - 1000pc - Rs250",
                        "Tuppada Batti - 100pc - Rs250",
                        "Gejje Vastra - 100pc - Rs250",
                        "Janiwara - 10pc - Rs100",
                        "Gopi Chandana - 10pc - Rs100"
                        ], email, number)

                else:
                    pass
            else:
               pass
    elif option == "General enquiries":
        general_enquiries()
    # Add more options handling for "About us" and "General enquiries" if needed

if __name__ == "__main__":
    main()
