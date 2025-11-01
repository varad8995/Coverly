import api from "../interceptor/interceptor"

const generateThumbnail = async (data) => {
    try {
        var response = await api.post("/api/upload-prompt", data);
        return response.data;
    }
    catch (error) {
        console.error("Error fetching the data");
        throw error;
    }
}

export { generateThumbnail };