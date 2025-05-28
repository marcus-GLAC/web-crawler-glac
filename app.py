# app.py
import streamlit as st
import asyncio
from supabase import create_client, Client
from crawl4ai import AsyncWebCrawler
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# MUST BE FIRST: Configure Streamlit page
st.set_page_config(
    page_title="Web Crawler App",
    page_icon="🕷️",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        st.error("Missing Supabase credentials in environment variables")
        return None
    return create_client(url, key)

supabase = init_supabase()

# Authentication functions
def sign_up(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        return {"error": str(e)}

def sign_in(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response
    except Exception as e:
        return {"error": str(e)}

def sign_out():
    try:
        supabase.auth.sign_out()
        return True
    except Exception as e:
        return False

# Crawling functions
async def crawl_url(url):
    """Crawl content from a given URL using Crawl4AI"""
    try:
        # Configure browser for Docker environment
        browser_config = {
            "headless": True,
            "verbose": True,
            "browser_type": "chromium",
            "chrome_channel": "chrome",
            "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        async with AsyncWebCrawler(**browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                word_count_threshold=10,
                extraction_strategy="NoExtractionStrategy",
                chunking_strategy="RegexChunking"
            )
            
            return {
                "success": True,
                "url": url,
                "title": result.metadata.get("title", "No title") if result.metadata else "No title",
                "content": result.markdown if result.markdown else "No content extracted",
                "links": result.links if hasattr(result, 'links') and result.links else [],
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "timestamp": datetime.now().isoformat()
        }

def save_crawl_result(user_id, crawl_data):
    """Save crawl result to Supabase with update if exists"""
    try:
        # Check if URL already exists
        existing = supabase.table('crawl_results')\
                         .select('id')\
                         .eq('user_id', user_id)\
                         .eq('url', crawl_data["url"])\
                         .execute()
        
        if existing.data:
            # Update existing record
            response = supabase.table('crawl_results').update({
                "title": crawl_data.get("title", ""),
                "content": crawl_data.get("content", ""),
                "links": json.dumps(crawl_data.get("links", [])),
                "success": crawl_data["success"],
                "error_message": crawl_data.get("error", ""),
                "created_at": crawl_data["timestamp"]
            }).eq('id', existing.data[0]['id']).execute()
        else:
            # Insert new record
            response = supabase.table('crawl_results').insert({
                "user_id": user_id,
                "url": crawl_data["url"],
                "title": crawl_data.get("title", ""),
                "content": crawl_data.get("content", ""),
                "links": json.dumps(crawl_data.get("links", [])),
                "success": crawl_data["success"],
                "error_message": crawl_data.get("error", ""),
                "created_at": crawl_data["timestamp"]
            }).execute()
        
        return response
    except Exception as e:
        st.error(f"Error saving crawl result: {str(e)}")
        return None

def get_user_crawl_history(user_id):
    """Get crawl history for a user"""
    try:
        response = supabase.table('crawl_results').select("*").eq('user_id', user_id).order('created_at', desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching crawl history: {str(e)}")
        return []

def delete_crawl_result(result_id):
    """Delete a specific crawl result"""
    try:
        response = supabase.table('crawl_results').delete().eq('id', result_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting crawl result: {str(e)}")
        return False

def clear_all_history(user_id):
    """Delete all history for a user"""
    try:
        response = supabase.table('crawl_results').delete().eq('user_id', user_id).execute()
        return True
    except Exception as e:
        st.error(f"Error clearing history: {str(e)}")
        return False

# Streamlit UI
def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Check if user is already authenticated
    if supabase and supabase.auth.get_user():
        st.session_state.authenticated = True
        st.session_state.user = supabase.auth.get_user().user
    
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        show_main_app()

def show_auth_page():
    st.title("🕷️ Web Crawler Authentication")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        st.subheader("Sign In")
        with st.form("signin_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
            
            if submit:
                if email and password:
                    with st.spinner("Signing in..."):
                        result = sign_in(email, password)
                        if "error" not in result:
                            st.session_state.authenticated = True
                            st.session_state.user = result.user
                            st.success("Signed in successfully!")
                            st.rerun()
                        else:
                            st.error(f"Sign in failed: {result['error']}")
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("Sign Up")
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if email and password and confirm_password:
                    if password == confirm_password:
                        with st.spinner("Creating account..."):
                            result = sign_up(email, password)
                            if "error" not in result:
                                st.success("Account created successfully! Please check your email for verification.")
                            else:
                                st.error(f"Sign up failed: {result['error']}")
                    else:
                        st.error("Passwords do not match")
                else:
                    st.error("Please fill in all fields")

def show_main_app():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🕷️ Scrawl4AI - Web Crawler")
    with col2:
        if st.button("Sign Out"):
            sign_out()
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
    
    # User info
    if st.session_state.user:
        st.info(f"Welcome, {st.session_state.user.email}!")
    
    # Main tabs
    tab1, tab2 = st.tabs(["🔍 Crawl Website", "📊 Crawl History"])
    
    with tab1:
        show_crawl_interface()
    
    with tab2:
        show_crawl_history()

def show_crawl_interface():
    st.subheader("Crawl Website Content")
    
    # URL input
    col1, col2 = st.columns([3, 1])
    with col1:
        url = st.text_input("Enter URL to crawl:", placeholder="https://example.com")
    with col2:
        crawl_button = st.button("🚀 Start Crawling", type="primary")
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        include_links = st.checkbox("Extract all links", value=True)
        max_depth = st.slider("Max crawl depth", 1, 5, 1)
        wait_time = st.slider("Wait time (seconds)", 1, 10, 3)
    
    if crawl_button and url:
        if url.startswith(('http://', 'https://')):
            with st.spinner("🕷️ Crawling website... This may take a few moments."):
                # Run async crawl function
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(crawl_url(url))
                loop.close()
                
                # Display results
                if result["success"]:
                    st.success("✅ Crawling completed successfully!")
                    
                    # Save to database
                    if st.session_state.user:
                        save_crawl_result(st.session_state.user.id, result)
                    
                    # Display content
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.subheader("📄 Extracted Content")
                        with st.expander("View Content", expanded=True):
                            st.markdown(result["content"][:2000] + "..." if len(result["content"]) > 2000 else result["content"])
                    
                    with col2:
                        st.subheader("📊 Summary")
                        st.metric("Title", result["title"])
                        st.metric("Content Length", f"{len(result['content'])} chars")
                        st.metric("Links Found", len(result.get("links", [])))
                        
                        # Download options
                        st.subheader("💾 Download")
                        st.download_button(
                            label="Download as Text",
                            data=result["content"],
                            file_name=f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
                        
                        st.download_button(
                            label="Download as JSON",
                            data=json.dumps(result, indent=2),
                            file_name=f"crawl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    
                    # Show extracted links - FIX FOR THE ERROR
                    links = result.get("links", [])
                    if links and isinstance(links, list):
                        st.subheader("🔗 Extracted Links")
                        # Safely slice the links list
                        display_links = links[:10]  # Show first 10 links
                        for i, link in enumerate(display_links):
                            if isinstance(link, str):
                                st.markdown(f"{i+1}. [{link}]({link})")
                            else:
                                st.markdown(f"{i+1}. {str(link)}")
                        
                        if len(links) > 10:
                            st.info(f"... and {len(links) - 10} more links")
                    elif links:
                        st.subheader("🔗 Extracted Links")
                        st.info("Links found but in unexpected format")
                
                else:
                    st.error(f"❌ Crawling failed: {result['error']}")
        else:
            st.error("Please enter a valid URL starting with http:// or https://")

def show_crawl_history():
    st.subheader("📊 Your Crawl History")
    
    if st.session_state.user:
        history = get_user_crawl_history(st.session_state.user.id)
        
        if history:
            # Clear all history button
            if st.button("🗑️ Clear All History", type="secondary"):
                if clear_all_history(st.session_state.user.id):
                    st.success("All history cleared!")
                    st.rerun()
                else:
                    st.error("Failed to clear history")
            
            for item in history:
                with st.expander(f"{'✅' if item['success'] else '❌'} {item['url']} - {item['created_at'][:19]}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**Title:** {item['title']}")
                        st.write(f"**URL:** {item['url']}")
                        st.write(f"**Timestamp:** {item['created_at']}")
                        if not item['success']:
                            st.error(f"Error: {item['error_message']}")
                    
                    with col2:
                        if item['success']:
                            st.metric("Content Length", f"{len(item['content'])} chars")
                            # Fix for links parsing from JSON
                            try:
                                links_data = json.loads(item['links']) if item['links'] else []
                                links_count = len(links_data) if isinstance(links_data, list) else 0
                            except (json.JSONDecodeError, TypeError):
                                links_count = 0
                            st.metric("Links Found", links_count)
                    
                    with col3:
                        # Re-crawl button
                        if st.button("🔄 Re-crawl", key=f"recrawl_{item['id']}"):
                            with st.spinner(f"Re-crawling {item['url']}..."):
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                new_result = loop.run_until_complete(crawl_url(item['url']))
                                loop.close()
                                
                                if new_result["success"]:
                                    save_crawl_result(st.session_state.user.id, new_result)
                                    st.success("Re-crawled successfully!")
                                    st.rerun()
                        
                        # Delete button
                        if st.button("❌ Delete", key=f"delete_{item['id']}"):
                            if delete_crawl_result(item['id']):
                                st.success("Item deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete item")
                        
                        # View content button
                        if st.button("📄 View Content", key=f"view_{item['id']}"):
                            st.text_area("Content:", item['content'], height=200)
        else:
            st.info("No crawl history found. Start crawling some websites!")
    else:
        st.error("User not found")

if __name__ == "__main__":
    main()