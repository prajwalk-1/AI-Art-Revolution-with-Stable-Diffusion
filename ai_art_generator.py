# Import necessary libraries
import streamlit as st
from diffusers import DiffusionPipeline  # Import the DiffusionPipeline class from the diffusers library
import torch  # Import the torch library for tensor operations
import matplotlib.pyplot as plt  # Import for image visualization
from PIL import Image  # Import to display image in Streamlit
import io  # Import for image buffer management

# Set Streamlit title
st.title("Stable Diffusion Image Generator")

# Streamlit sidebar for input parameters
st.sidebar.header("Input Settings")

# Text input for the prompt
prompt = st.sidebar.text_input("Prompt", "A vibrant sunset over the city skyline with silhouetted buildings.")

# Button to generate image
generate = st.sidebar.button("Generate Image")

# Initialize the base pipeline outside the button to avoid reloading the model every time
@st.cache_resource
def load_pipeline():
    # Load the pre-trained model using the 'stable-diffusion-xl-base-1.0' pipeline
    pipe = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",  # Specify the model checkpoint to load for the base pipeline
        torch_dtype=torch.float16,  # Set the data type for tensors to float16 for optimized performance
        use_safetensors=True,  # Enable safe tensors for numerical stability
        variant="fp16"  # Use the FP16 variant to optimize performance
    )
    pipe.to("cuda")  # Move the pipeline to GPU for faster processing
    return pipe

pipe = load_pipeline()

# Function to generate and display image
def generate_image(prompt):
    try:
        # Clear CUDA memory cache
        torch.cuda.empty_cache()
        
        # Generate image from the pipeline with reduced resolution
        images = pipe(prompt=prompt, height=256, width=256).images[0]
        
        # Convert to PIL Image for display in Streamlit
        buffer = io.BytesIO()
        images.save(buffer, format="PNG")
        buffer.seek(0)
        return Image.open(buffer)
    except RuntimeError as e:
        # Handle CUDA out-of-memory error
        if "out of memory" in str(e):
            st.error("CUDA out of memory. Try reducing image size or restart the application.")
        else:
            st.error(f"An error occurred: {str(e)}")

# If the generate button is pressed
if generate:
    st.subheader("Generated Image")
    # Generate and display image based on prompt
    generated_image = generate_image(prompt)
    if generated_image:
        st.image(generated_image, caption="Generated by Stable Diffusion", use_column_width=True)