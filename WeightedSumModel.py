import streamlit as st
import rasterio
import numpy as np
import gc  # Garbage collection
import matplotlib.pyplot as plt

# Title and Introduction
st.title("Site Suitability Tool")
st.markdown(
    "Upload processed GeoTIFF files to dynamically calculate suitability scores using different weights."")

@st.cache_data(max_entries=5)
def load_raster(file):
    """Loads and caches raster data to reduce memory usage."""
    with rasterio.MemoryFile(file.read()) as memfile:
        with memfile.open() as src:
            data = src.read(1, out_dtype=np.float32)  # Read as float32 to save memory
    return data

# Step 1: Upload Processed GeoTIFF Files
st.header("Step 1: Upload Processed Rasters")
uploaded_files = st.file_uploader(
    "Upload processed raster layers (GeoTIFF files)", type=["tif", "tiff"], accept_multiple_files=True
)

raster_data = {}  # Dictionary to store loaded raster data

if uploaded_files:
    st.success(f"Uploaded {len(uploaded_files)} files.")

    for file in uploaded_files:
        try:
            data = load_raster(file)
            raster_data[file.name] = data
            st.write(f"Loaded: {file.name} | Shape: {data.shape}")
        except Exception as e:
            st.error(f"Error loading {file.name}: {e}")
else:
    st.warning("Please upload at least one GeoTIFF file to proceed.")

# Step 2: Define Weights and Calculate Scores
if raster_data:
    st.header("Step 2: Define Weights")

    # Prompt user for weights
    weights = {}
    for layer_name in raster_data.keys():
        weight = st.number_input(
            f"Weight for {layer_name}", min_value=0.0, max_value=1.0, step=0.1, value=1.0 / len(raster_data)
        )
        weights[layer_name] = weight

    # Ensure weights sum to 1
    if not np.isclose(sum(weights.values()), 1.0):
        st.warning("The sum of weights should equal 1. Please adjust them.")

    # Calculate suitability scores if weights are valid
    if st.button("Calculate Suitability Scores") and np.isclose(sum(weights.values()), 1.0):
        st.header("Suitability Scores")

        # Combine rasters using weighted sum in a memory-efficient way
        shape = next(iter(raster_data.values())).shape  # Get shape from first raster
        combined_array = np.zeros(shape, dtype=np.float32)

        for layer_name, data in raster_data.items():
            combined_array += weights[layer_name] * data

        st.success("Suitability scores calculated successfully!")

        # Display suitability scores as a heatmap
        plt.figure(figsize=(10, 8))
        plt.imshow(combined_array, cmap='viridis', interpolation='nearest')
        plt.colorbar(label='Suitability Score')
        plt.title("Weighted Suitability Scores")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")
        st.pyplot(plt)

        # Perform garbage collection to free memory
        del raster_data  # Delete dictionary holding raster arrays
        gc.collect()

        # Save the suitability scores as a GeoTIFF
        st.header("Download Suitability Scores")
        output_filename = st.text_input("Output filename (e.g., suitability.tif):", "suitability.tif")
        if st.button("Download GeoTIFF"):
            try:
                with rasterio.open(uploaded_files[0]) as ref:
                    meta = ref.meta.copy()
                    meta.update(dtype=rasterio.float32, count=1)

                    with rasterio.open(output_filename, "w", **meta) as dst:
                        dst.write(combined_array.astype(rasterio.float32), 1)
                    st.success(f"GeoTIFF saved as {output_filename}.")
            except Exception as e:
                st.error(f"Error saving GeoTIFF: {e}")

        # Clean up memory
        del combined_array
        gc.collect()

# import streamlit as st
# import rasterio
# import numpy as np
# import gc  # Garbage collection
# import matplotlib.pyplot as plt

# # Title and Introduction
# st.title("Site Suitability Tool")
# st.markdown(
#     "Upload processed GeoTIFF files to dynamically calculate suitability scores using different weights."
# )

# # Step 1: Upload Processed GeoTIFF Files
# st.header("Step 1: Upload Processed Rasters")
# uploaded_files = st.file_uploader(
#     "Upload processed raster layers (GeoTIFF files)", type=["tif", "tiff"], accept_multiple_files=True
# )

# raster_data = {}  # Dictionary to store loaded raster data

# if uploaded_files:
#     st.success(f"Uploaded {len(uploaded_files)} files.")

#     for file in uploaded_files:
#         try:
#             # Load raster file in memory-efficient way
#             with rasterio.MemoryFile(file.read()) as memfile:
#                 with memfile.open() as src:
#                     data = src.read(1, out_dtype=np.float32)  # Read as float32 to save memory
#                     raster_data[file.name] = data
#                     st.write(f"Loaded: {file.name} | Shape: {data.shape} | CRS: {src.crs}")
#         except Exception as e:
#             st.error(f"Error loading {file.name}: {e}")
# else:
#     st.warning("Please upload at least one GeoTIFF file to proceed.")

# # Step 2: Define Weights and Calculate Scores
# if raster_data:
#     st.header("Step 2: Define Weights")

#     # Prompt user for weights
#     weights = {}
#     for layer_name in raster_data.keys():
#         weight = st.number_input(
#             f"Weight for {layer_name}", min_value=0.0, max_value=1.0, step=0.1, value=1.0 / len(raster_data)
#         )
#         weights[layer_name] = weight

#     # Ensure weights sum to 1
#     if not np.isclose(sum(weights.values()), 1.0):
#         st.warning("The sum of weights should equal 1. Please adjust them.")

#     # Calculate suitability scores if weights are valid
#     if st.button("Calculate Suitability Scores") and np.isclose(sum(weights.values()), 1.0):
#         st.header("Suitability Scores")

#         # Combine rasters using weighted sum in a memory-efficient way
#         shape = next(iter(raster_data.values())).shape  # Get shape from first raster
#         combined_array = np.zeros(shape, dtype=np.float32)

#         for layer_name, data in raster_data.items():
#             combined_array += weights[layer_name] * data

#         st.success("Suitability scores calculated successfully!")

#         # Display suitability scores as a heatmap
#         plt.figure(figsize=(10, 8))
#         plt.imshow(combined_array, cmap='viridis', interpolation='nearest')
#         plt.colorbar(label='Suitability Score')
#         plt.title("Weighted Suitability Scores")
#         plt.xlabel("X Coordinate")
#         plt.ylabel("Y Coordinate")
#         st.pyplot(plt)

#         # Perform garbage collection to free memory
#         del raster_data  # Delete dictionary holding raster arrays
#         gc.collect()

#         # Save the suitability scores as a GeoTIFF
#         st.header("Download Suitability Scores")
#         output_filename = st.text_input("Output filename (e.g., suitability.tif):", "suitability.tif")
#         if st.button("Download GeoTIFF"):
#             try:
#                 with rasterio.open(uploaded_files[0]) as ref:
#                     meta = ref.meta.copy()
#                     meta.update(dtype=rasterio.float32, count=1)

#                     with rasterio.open(output_filename, "w", **meta) as dst:
#                         dst.write(combined_array.astype(rasterio.float32), 1)
#                     st.success(f"GeoTIFF saved as {output_filename}.")
#             except Exception as e:
#                 st.error(f"Error saving GeoTIFF: {e}")

#         # Clean up memory
#         del combined_array
#         gc.collect()
