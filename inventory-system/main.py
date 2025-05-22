import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

class Product:
    """Class representing a product in the inventory"""
    
    def __init__(self, product_id, name, category, quantity, price, last_updated=None):
        """Initialize a product
        
        Args:
            product_id (str): Unique identifier for the product
            name (str): Name of the product
            category (str): Category of the product
            quantity (int): Available quantity in inventory
            price (float): Price per unit
            last_updated (str, optional): Timestamp when product was last updated
        """
        self.product_id = product_id
        self.name = name
        self.category = category
        self.quantity = quantity
        self.price = price
        self.last_updated = last_updated if last_updated else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        """Convert product to dictionary for storage
        
        Returns:
            dict: Dictionary representation of product
        """
        return {
            "product_id": self.product_id,
            "name": self.name,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a Product instance from a dictionary
        
        Args:
            data (dict): Dictionary containing product data
            
        Returns:
            Product: New Product instance
        """
        return cls(
            product_id=data["product_id"],
            name=data["name"],
            category=data["category"],
            quantity=data["quantity"],
            price=data["price"],
            last_updated=data["last_updated"]
        )


class InventoryManager:
    """Class for managing the inventory of products"""
    
    def __init__(self, file_path="inventory_data.json"):
        """Initialize the inventory manager
        
        Args:
            file_path (str): Path to the JSON file for data storage
        """
        self.file_path = file_path
        self.products = {}
        self.load_inventory()
    
    def load_inventory(self):
        """Load inventory data from file if it exists"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as file:
                    data = json.load(file)
                    self.products = {
                        pid: Product.from_dict(pdata) 
                        for pid, pdata in data.items()
                    }
            except (json.JSONDecodeError, KeyError) as e:
                st.error(f"Error loading inventory data: {e}")
                self.products = {}
    
    def save_inventory(self):
        """Save inventory data to file"""
        data = {
            pid: product.to_dict() 
            for pid, product in self.products.items()
        }
        with open(self.file_path, 'w') as file:
            json.dump(data, file, indent=4)
    
    def add_product(self, product):
        """Add a new product to the inventory
        
        Args:
            product (Product): Product to add
            
        Returns:
            bool: True if added successfully, False if product_id already exists
        """
        if product.product_id in self.products:
            return False
        
        self.products[product.product_id] = product
        self.save_inventory()
        return True
    
    def update_product(self, product_id, name=None, category=None, quantity=None, price=None):
        """Update an existing product
        
        Args:
            product_id (str): ID of product to update
            name (str, optional): New name
            category (str, optional): New category
            quantity (int, optional): New quantity
            price (float, optional): New price
            
        Returns:
            bool: True if updated successfully, False if product not found
        """
        if product_id not in self.products:
            return False
        
        product = self.products[product_id]
        
        if name is not None:
            product.name = name
        if category is not None:
            product.category = category
        if quantity is not None:
            product.quantity = quantity
        if price is not None:
            product.price = price
            
        product.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_inventory()
        return True
    
    def delete_product(self, product_id):
        """Delete a product from inventory
        
        Args:
            product_id (str): ID of product to delete
            
        Returns:
            bool: True if deleted successfully, False if product not found
        """
        if product_id not in self.products:
            return False
        
        del self.products[product_id]
        self.save_inventory()
        return True
    
    def get_product(self, product_id):
        """Get a product by ID
        
        Args:
            product_id (str): ID of product to retrieve
            
        Returns:
            Product or None: Product if found, None otherwise
        """
        return self.products.get(product_id)
    
    def get_all_products(self):
        """Get all products in inventory
        
        Returns:
            list: List of all products
        """
        return list(self.products.values())
    
    def get_low_stock_products(self, threshold=5):
        """Get products with stock below threshold
        
        Args:
            threshold (int): Stock threshold
            
        Returns:
            list: List of products below threshold
        """
        return [p for p in self.products.values() if p.quantity <= threshold]
    
    def search_products(self, query):
        """Search products by name or category
        
        Args:
            query (str): Search term
            
        Returns:
            list: List of matching products
        """
        query = query.lower()
        return [
            p for p in self.products.values() 
            if query in p.name.lower() or query in p.category.lower()
        ]


def main():
    # Setup page configuration
    st.set_page_config(
        page_title="Inventory Management System",
        page_icon="📦",
        layout="wide"
    )
    
    # Initialize inventory manager in session state if it doesn't exist
    if "inventory_manager" not in st.session_state:
        st.session_state.inventory_manager = InventoryManager()
    
    # Main title
    st.title("📦 Inventory Management System")
    
    # Create tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs(["View Inventory", "Add Product", "Update Product", "Delete Product"])
    
    # Tab 1: View Inventory
    with tab1:
        st.header("Current Inventory")
        
        # Search functionality
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input("Search products by name or category")
        with search_col2:
            st.write("")
            st.write("")
            is_searching = st.checkbox("Search")
        
        # Display inventory as a dataframe
        if is_searching and search_query:
            products = st.session_state.inventory_manager.search_products(search_query)
            if not products:
                st.info(f"No products found matching '{search_query}'")
        else:
            products = st.session_state.inventory_manager.get_all_products()
        
        if products:
            # Convert products to dataframe for display
            products_data = [p.to_dict() for p in products]
            df = pd.DataFrame(products_data)
            
            # Add total value column
            df["total_value"] = df["quantity"] * df["price"]
            
            # Reorder and format columns
            df = df[["product_id", "name", "category", "quantity", "price", "total_value", "last_updated"]]
            df = df.rename(columns={
                "product_id": "ID",
                "name": "Product Name",
                "category": "Category",
                "quantity": "Quantity",
                "price": "Unit Price ($)",
                "total_value": "Total Value ($)",
                "last_updated": "Last Updated"
            })
            
            st.dataframe(df, use_container_width=True)
            
            # Show inventory statistics
            st.subheader("Inventory Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Products", len(products))
            with col2:
                total_items = sum(p.quantity for p in products)
                st.metric("Total Items", total_items)
            with col3:
                total_value = sum(p.quantity * p.price for p in products)
                st.metric("Total Value ($)", f"{total_value:.2f}")
            with col4:
                low_stock = len(st.session_state.inventory_manager.get_low_stock_products())
                st.metric("Low Stock Items", low_stock)
            
            # Show low stock warning
            if low_stock > 0:
                st.warning(f"⚠️ {low_stock} products are running low on stock (5 or fewer items)")
        else:
            st.info("No products in inventory. Add products using the 'Add Product' tab.")
    
    # Tab 2: Add Product
    with tab2:
        st.header("Add New Product")
        
        with st.form("add_product_form"):
            # Auto-generate a product ID based on timestamp (can be improved)
            suggested_id = f"P{int(datetime.now().timestamp())}"
            product_id = st.text_input("Product ID", value=suggested_id)
            name = st.text_input("Product Name")
            
            col1, col2 = st.columns(2)
            with col1:
                category = st.selectbox(
                    "Category", 
                    options=["Electronics", "Clothing", "Food", "Furniture", "Office Supplies", "Other"]
                )
            with col2:
                quantity = st.number_input("Quantity", min_value=0, value=10)
            
            price = st.number_input("Unit Price ($)", min_value=0.01, step=0.01, format="%.2f")
            
            submitted = st.form_submit_button("Add Product")
            
            if submitted:
                if not name:
                    st.error("Product name is required!")
                elif not product_id:
                    st.error("Product ID is required!")
                else:
                    # Create a new product
                    new_product = Product(
                        product_id=product_id,
                        name=name,
                        category=category,
                        quantity=int(quantity),
                        price=float(price)
                    )
                    
                    # Add to inventory
                    if st.session_state.inventory_manager.add_product(new_product):
                        st.success(f"Product '{name}' added successfully!")
                        # Clear form
                        st.form_submit_button("Add Another Product")
                    else:
                        st.error(f"Product ID '{product_id}' already exists!")
    
    # Tab 3: Update Product
    with tab3:
        st.header("Update Product")
        
        # Get list of products for selection
        products = st.session_state.inventory_manager.get_all_products()
        product_options = {f"{p.product_id} - {p.name}": p.product_id for p in products}
        
        if not product_options:
            st.info("No products in inventory to update. Add products using the 'Add Product' tab.")
        else:
            # Select product to update
            selected_product_display = st.selectbox(
                "Select Product to Update",
                options=list(product_options.keys())
            )
            selected_product_id = product_options[selected_product_display]
            
            # Get current product details
            product = st.session_state.inventory_manager.get_product(selected_product_id)
            
            if product:
                with st.form("update_product_form"):
                    st.subheader(f"Update {product.name}")
                    
                    name = st.text_input("Product Name", value=product.name)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        category = st.selectbox(
                            "Category", 
                            options=["Electronics", "Clothing", "Food", "Furniture", "Office Supplies", "Other"],
                            index=["Electronics", "Clothing", "Food", "Furniture", "Office Supplies", "Other"].index(product.category)
                            if product.category in ["Electronics", "Clothing", "Food", "Furniture", "Office Supplies", "Other"] else 5
                        )
                    with col2:
                        quantity = st.number_input("Quantity", min_value=0, value=product.quantity)
                    
                    price = st.number_input("Unit Price ($)", min_value=0.01, step=0.01, value=product.price, format="%.2f")
                    
                    submitted = st.form_submit_button("Update Product")
                    
                    if submitted:
                        if not name:
                            st.error("Product name is required!")
                        else:
                            # Update the product
                            if st.session_state.inventory_manager.update_product(
                                product_id=selected_product_id,
                                name=name,
                                category=category,
                                quantity=int(quantity),
                                price=float(price)
                            ):
                                st.success(f"Product '{name}' updated successfully!")
                            else:
                                st.error("Failed to update product!")
    
    # Tab 4: Delete Product
    with tab4:
        st.header("Delete Product")
        
        # Get list of products for selection
        products = st.session_state.inventory_manager.get_all_products()
        product_options = {f"{p.product_id} - {p.name}": p.product_id for p in products}
        
        if not product_options:
            st.info("No products in inventory to delete. Add products using the 'Add Product' tab.")
        else:
            # Select product to delete
            selected_product_display = st.selectbox(
                "Select Product to Delete",
                options=list(product_options.keys())
            )
            selected_product_id = product_options[selected_product_display]
            
            # Get current product details
            product = st.session_state.inventory_manager.get_product(selected_product_id)
            
            if product:
                # Display product details
                st.subheader("Product Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID:** {product.product_id}")
                    st.write(f"**Name:** {product.name}")
                    st.write(f"**Category:** {product.category}")
                with col2:
                    st.write(f"**Quantity:** {product.quantity}")
                    st.write(f"**Price:** ${product.price:.2f}")
                    st.write(f"**Last Updated:** {product.last_updated}")
                
                # Confirm deletion
                st.warning("Are you sure you want to delete this product? This action cannot be undone.")
                if st.button("Delete Product", type="primary"):
                    if st.session_state.inventory_manager.delete_product(selected_product_id):
                        st.success(f"Product '{product.name}' deleted successfully!")
                        # Force a rerun to update the UI
                        st.rerun()
                    else:
                        st.error("Failed to delete product!")


if __name__ == "__main__":
    main()