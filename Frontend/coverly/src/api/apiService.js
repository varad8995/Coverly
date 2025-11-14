import api from "../interceptor/interceptor"

const generateThumbnail = async (data) => {
    try {
        var response = await api.post("api/upload-prompt", data);
        return {
            success: true,
            message: "Thumbnail generated successfully",
            data: response.data
        };
        // return response.data;
    }
    catch (error) {
        let message = "An unexpected error occurred. Please try again.";
        if (error.response) {
            const status = error.response.status;

            if (status === 403) {
                message = error.response.detail;
            } else if (status === 400) {
                message = "Invalid request. Please check your input.";
            } else if (error.response.data?.message) {
                message = error.response.data.detail;
            }
        }

        return {
            success: false,
            message,
            data: null
        };
    }
}

const downloadPhoto = async (presignedUrl) => {
    try {
        const response = await api.post(
            "api/download-photo",
            { presigned_url: presignedUrl },
            { responseType: "blob" } // IMPORTANT
        );

        // Convert blob → downloadable file
        const blob = new Blob([response.data]);
        const downloadUrl = window.URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = "photo.jpg";
        link.click();

        window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
        console.error("Download failed:", err);
    }
};

export { generateThumbnail, downloadPhoto };