import axios from "axios";

const baseURL = "/api/annotator/";

export default {
  getData(id, params) {
    return axios.get(`${baseURL}/data/${id}`, {
      params: {
        ...params
      }
    });
  }
};
