import axios from "axios";

const baseURL = "/api/dataset";

export default {
  allData(params) {
    return axios.get(`${baseURL}/data`, {
      params: {
        ...params
      }
    });
  },
  getData(id, params) {
    return axios.get(`${baseURL}/${id}/data`, {
      params: {
        ...params
      }
    });
  },
  create(name, categories) {
    return axios.post(`${baseURL}/?name=${name}`, {
      categories: categories
    });
  },
  change(dataset_id) {
    return axios.put(`${baseURL}/?dataset_id=${dataset_id}`);
  },
  generate(id, body) {
    return axios.post(`${baseURL}/${id}/generate`, {
      ...body
    });
  },
  scan(id) {
    return axios.get(`${baseURL}/${id}/scan`);
  },
  exportingCOCO(id, categories) {
    return axios.get(`${baseURL}/${id}/export?categories=${categories}`);
  },
  getCoco(id) {
    return axios.get(`${baseURL}/${id}/coco`);
  },
  uploadCoco(id, file) {
    let form = new FormData();
    form.append("coco", file);

    return axios.post(`${baseURL}/${id}/coco`, form, {
      headers: {
        "Content-Type": "multipart/form-data"
      }
    });
  },
  export(id, format) {
    return axios.get(`${baseURL}/${id}/${format}`);
  },
  getUsers(id) {
    return axios.get(`${baseURL}/${id}/users`);
  },
  getStats(id) {
    return axios.get(`${baseURL}/${id}/stats`);
  },
  getExports(id) {
    return axios.get(`${baseURL}/${id}/exports`);
  },
  getPredictions(id) {
    return axios.get(`${baseURL}/${id}/predict`);
  },
  makePredictions(id) {
    return axios.post(`${baseURL}/${id}/predict`);
  },
  updateAnnotationsDB(id) {
    return axios.put(`${baseURL}/${id}/predict`);
  }
};
