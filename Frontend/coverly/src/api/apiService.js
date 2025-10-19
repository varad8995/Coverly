import api from "../interceptor/interceptor"

const generateThumbail = async (data) => {
    try {
        var response = await api.post("", data);
        return response.data;
    }
    catch (error) {
        console.error("Error fetching the data");
        throw error;
    }
}

export { generateThumbail };