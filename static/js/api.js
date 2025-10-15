/**
 * API service for the Hierarchical Data Explorer.
 *
 * This module handles all API communication including HTTP requests,
 * error handling, and data transformation.
 */

class ApiService {
    constructor() {
        this.baseURL = '';
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    /**
     * Make an HTTP request with error handling
     * @param {string} url - The API endpoint
     * @param {Object} options - Request options (method, headers, body, etc.)
     * @returns {Promise<Object>} The response data
     */
    async request(url, options = {}) {
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options
        };

        try {
            const response = await fetch(this.baseURL + url, config);

            if (!response.ok) {
                let data;
                try {
                    data = await response.json();
                } catch {
                    throw new Error(`HTTP ${response.status}`);
                }
                throw new Error(data.detail || `HTTP ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error(`API request failed: ${url}`, error);
            throw error;
        }
    }

    /**
     * GET request
     * @param {string} url - The API endpoint
     * @param {Object} options - Additional request options
     * @returns {Promise<Object>} The response data
     */
    async get(url, options = {}) {
        return this.request(url, { method: 'GET', ...options });
    }

    /**
     * POST request
     * @param {string} url - The API endpoint
     * @param {Object} data - The request body data
     * @param {Object} options - Additional request options
     * @returns {Promise<Object>} The response data
     */
    async post(url, data, options = {}) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    }

    /**
     * PUT request
     * @param {string} url - The API endpoint
     * @param {Object} data - The request body data
     * @param {Object} options - Additional request options
     * @returns {Promise<Object>} The response data
     */
    async put(url, data, options = {}) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options
        });
    }

    /**
     * DELETE request
     * @param {string} url - The API endpoint
     * @param {Object} options - Additional request options
     * @returns {Promise<Object>} The response data
     */
    async delete(url, options = {}) {
        return this.request(url, { method: 'DELETE', ...options });
    }
}

/**
 * Customer API endpoints and operations
 */
class CustomerService extends ApiService {
    async getAll() {
        return this.get('/api/customers');
    }

    async getById(id) {
        return this.get(`/api/customers/${encodeURIComponent(id)}`);
    }

    async create(customerData) {
        return this.post('/api/customers', customerData);
    }

    async update(id, customerData) {
        return this.put(`/api/customers/${encodeURIComponent(id)}`, customerData);
    }

    async delete(id) {
        return this.delete(`/api/customers/${encodeURIComponent(id)}`);
    }
}

/**
 * Project API endpoints and operations
 */
class ProjectService extends ApiService {
    async getByCustomer(customerId) {
        return this.get(`/api/projects/${encodeURIComponent(customerId)}`);
    }

    async getById(id) {
        return this.get(`/api/projects/${encodeURIComponent(id)}`);
    }

    async create(projectData) {
        return this.post('/api/projects', projectData);
    }

    async update(id, projectData) {
        return this.put(`/api/projects/${encodeURIComponent(id)}`, projectData);
    }

    async delete(id) {
        return this.delete(`/api/projects/${encodeURIComponent(id)}`);
    }
}

/**
 * Quote API endpoints and operations
 */
class QuoteService extends ApiService {
    async getByProject(projectId) {
        return this.get(`/api/quotes/${encodeURIComponent(projectId)}`);
    }

    async getById(id) {
        return this.get(`/api/quotes/${encodeURIComponent(id)}`);
    }

    async create(quoteData) {
        return this.post('/api/quotes', quoteData);
    }

    async update(id, quoteData) {
        return this.put(`/api/quotes/${encodeURIComponent(id)}`, quoteData);
    }

    async delete(id) {
        return this.delete(`/api/quotes/${encodeURIComponent(id)}`);
    }
}

/**
 * Freight Request API endpoints and operations
 */
class FreightRequestService extends ApiService {
    async getByQuote(quoteId) {
        return this.get(`/api/freight-requests/${encodeURIComponent(quoteId)}`);
    }

    async getById(id) {
        return this.get(`/api/freight-requests/${encodeURIComponent(id)}`);
    }

    async create(freightRequestData) {
        return this.post('/api/freight-requests', freightRequestData);
    }

    async update(id, freightRequestData) {
        return this.put(`/api/freight-requests/${encodeURIComponent(id)}`, freightRequestData);
    }

    async delete(id) {
        return this.delete(`/api/freight-requests/${encodeURIComponent(id)}`);
    }
}

/**
 * Vendor API endpoints and operations
 */
class VendorService extends ApiService {
    async getAll() {
        return this.get('/api/vendors');
    }

    async getById(id) {
        return this.get(`/api/vendors/${encodeURIComponent(id)}`);
    }

    async create(vendorData) {
        return this.post('/api/vendors', vendorData);
    }

    async update(id, vendorData) {
        return this.put(`/api/vendors/${encodeURIComponent(id)}`, vendorData);
    }

    async delete(id) {
        return this.delete(`/api/vendors/${encodeURIComponent(id)}`);
    }
}

// Create singleton instances
const customerService = new CustomerService();
const projectService = new ProjectService();
const quoteService = new QuoteService();
const freightRequestService = new FreightRequestService();
const vendorService = new VendorService();

// Export services for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        ApiService,
        CustomerService,
        ProjectService,
        QuoteService,
        FreightRequestService,
        VendorService,
        customerService,
        projectService,
        quoteService,
        freightRequestService,
        vendorService
    };
}