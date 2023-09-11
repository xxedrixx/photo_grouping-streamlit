import os
import shutil
import streamlit as st
from PIL import Image
import face_recognition
import time

def perform_face_filtering(input_directory, output_directory, known_faces_directory):
    if not os.path.exists(input_directory) or not os.path.exists(known_faces_directory):
        st.error("Input directory or known faces directory does not exist.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Create a directory for images with no match
    no_match_directory = os.path.join(output_directory, "no_match")
    if not os.path.exists(no_match_directory):
        os.makedirs(no_match_directory)

    subfolders = [f for f in os.listdir(known_faces_directory) if os.path.isdir(os.path.join(known_faces_directory, f))]
    num_subfolders = len(subfolders)
    total_files = len(os.listdir(input_directory))
    processed_files = 0

    # Display progress
    progress_percentage = st.empty()
    

    # Iterate over the subdirectories in the known faces directory
    for person_name in os.listdir(known_faces_directory):
        person_directory = os.path.join(known_faces_directory, person_name)

        if not os.path.isdir(person_directory):
            continue  # Skip non-directory entries

        # Create a corresponding output directory for this person
        person_output_directory = os.path.join(output_directory, person_name)
        if not os.path.exists(person_output_directory):
            os.makedirs(person_output_directory)

        # Load the known face encodings for this person
        known_faces_encodings = []
        for file_name in os.listdir(person_directory):
            image = face_recognition.load_image_file(
                os.path.join(person_directory, file_name))
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                known_faces_encodings.extend(face_encodings)

        # Iterate over the input directory
        for file_name in os.listdir(input_directory):
            image_path = os.path.join(input_directory, file_name)

            # Load the input image
            image = face_recognition.load_image_file(image_path)

            # Find face locations and encodings in the image
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)

            # Flag to indicate if any match is found
            match_found = False

            # Iterate over the face encodings in the image
            for face_encoding in face_encodings:
                # Compare the face encoding with the known face encodings
                matches = face_recognition.compare_faces(
                    known_faces_encodings, face_encoding)

                if any(matches):
                    # Copy the image to the corresponding person's directory
                    shutil.copy2(image_path, person_output_directory)
                    st.write(
                        f"Image '{file_name}' contains a known face ({person_name}) and has been copied to ({person_output_directory}) directory.")
                    match_found = True
                    break

            # Update the progress bar
            processed_files += 1
            progress_percentage.progress((processed_files / total_files) / num_subfolders)

    if not match_found:
        # Move the image to the 'no_match' directory
        no_match_path = os.path.join(no_match_directory, file_name)
        shutil.copy2(image_path, no_match_path)
        st.write(
            f"Image '{file_name}' does not contain a known face and has been moved to 'no_match' folder.")

    st.success("Face filtering complete.")

# Streamlit UI
st.title("Face Filtering")

input_directory = st.text_input("Input Directory")
output_directory = st.text_input("Output Directory")
known_faces_directory = st.text_input("Known Faces Directory")

if st.button("Perform Face Filtering"):
    if input_directory and output_directory and known_faces_directory:
        perform_face_filtering(input_directory, output_directory, known_faces_directory)
    else:
        st.error("Please select all directories.")

st.write("**Input directory:** The folder where there are photos to be filtered")
st.write("**Output directory:** The folder to put the filtered photos")
st.write("**Known faces directory:** The folder that has the known faces")
