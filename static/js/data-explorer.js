/**
 * Main Data Explorer application component.
 *
 * This module contains the core application logic for managing
 * hierarchical data navigation, CRUD operations, and state management.
 */

// Import utility functions and API services
// Note: In a browser environment, these would be loaded via script tags

function dataExplorer() {
    return {
        // Data stores
        customers: [],
        projects: [],
        quotes: [],
        vendorQuotes: [],
        vendors: [],

        // Selected items
        selectedCustomer: null,
        selectedProject: null,
        selectedQuote: null,
        selectedVendorQuote: null,

        // Loading and error states
        loading: {
            customers: false,
            projects: false,
            quotes: false,
            vendorQuotes: false
        },

        error: {
            customers: null,
            projects: null,
            quotes: null,
            vendorQuotes: null
        },

        // UI state
        openAccordions: {
            customer: false,
            project: false,
            quote: false,
            vendor_quote: false
        },
        lastClickedLevel: null,

        // Modal state
        showModal: false,
        modalType: null,
        modalData: {},
        isEdit: false,
        editItemId: null,
        isSubmitting: false,
        validationErrors: {},

        /**
         * Initialize the application
         */
        init() {
            this.loadCustomers();
            this.loadVendors();
        },

        /**
         * Data loading methods
         */
        async loadCustomers() {
            await this.loadData('customers', '/api/customers');
        },

        async loadProjects(customerId) {
            await this.loadData('projects', `/api/projects/${customerId}`);
        },

        async loadQuotes(projectId) {
            await this.loadData('quotes', `/api/quotes/${projectId}`);
        },

        async loadVendorQuotes(quoteId) {
            await this.loadData('vendorQuotes', `/api/vendor-quotes/by-quote/${quoteId}`);
        },

        async loadVendors() {
            try {
                const response = await fetch('/api/vendors');
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                this.vendors = await response.json();
            } catch (error) {
                console.error('Error loading vendors:', error);
                this.vendors = [];
            }
        },

        /**
         * Generic data loading method
         */
        async loadData(type, url) {
            this.loading[type] = true;
            this.error[type] = null;

            try {
                const response = await fetch(url);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                this[type] = await response.json();
            } catch (error) {
                console.error(`Error loading ${type}:`, error);
                this.error[type] = `Failed to load ${type}`;
                this[type] = [];
            } finally {
                this.loading[type] = false;
            }
        },

        /**
         * Selection methods with cascading data loading and accordion coupling
         */
        async selectCustomer(customer) {
            this.selectedCustomer = customer;
            this.clearLowerSelections('customer');

            if (customer) {
                await this.loadProjects(customer.id);
                // Atomic accordion state update - open only customer accordion
                this.openOnlyAccordion('customer');
            }
        },

        async selectProject(project) {
            this.selectedProject = project;
            this.clearLowerSelections('project');

            if (project) {
                await this.loadQuotes(project.id);
                // Atomic accordion state update - open only project accordion
                this.openOnlyAccordion('project');
            }
        },

        async selectQuote(quote) {
            this.selectedQuote = quote;
            this.clearLowerSelections('quote');

            if (quote) {
                await this.loadVendorQuotes(quote.id);
                // Atomic accordion state update - open only quote accordion
                this.openOnlyAccordion('quote');
            }
        },

        selectVendorQuote(vendorQuote) {
            this.selectedVendorQuote = vendorQuote;
            if (vendorQuote) {
                // Atomic accordion state update - open only vendor_quote accordion
                this.openOnlyAccordion('vendor_quote');
            }
        },

        /**
         * Clear selections and data for lower hierarchy levels
         */
        clearLowerSelections(level) {
            switch(level) {
                case 'customer':
                    this.selectedProject = null;
                    this.selectedQuote = null;
                    this.selectedVendorQuote = null;
                    this.projects = [];
                    this.quotes = [];
                    this.vendorQuotes = [];
                    break;
                case 'project':
                    this.selectedQuote = null;
                    this.selectedVendorQuote = null;
                    this.quotes = [];
                    this.vendorQuotes = [];
                    break;
                case 'quote':
                    this.selectedVendorQuote = null;
                    this.vendorQuotes = [];
                    break;
            }
        },

        /**
         * Clear all selections and data
         */
        clearSelections() {
            this.selectedCustomer = null;
            this.selectedProject = null;
            this.selectedQuote = null;
            this.selectedVendorQuote = null;
            this.projects = [];
            this.quotes = [];
            this.vendorQuotes = [];
        },

        /**
         * Accordion management
         */
        toggleAccordion(section) {
            // Toggle the clicked accordion independently for manual control
            // Manual accordion interaction should NOT affect card selection
            this.openAccordions[section] = !this.openAccordions[section];
            // Don't update lastClickedLevel here - it should only be set by card clicks
        },

        // Open accordion based on hierarchy level when item is selected
        openAccordionForLevel(level) {
            // Only open the specific accordion for this level
            // This is used by card selection logic
            if (level && this.openAccordions.hasOwnProperty(level)) {
                this.openAccordions[level] = true;
                this.lastClickedLevel = level;
            }
        },

        closeAllAccordions() {
            Object.keys(this.openAccordions).forEach(key => {
                this.openAccordions[key] = false;
            });
        },

        // Atomic accordion state update to prevent flicker
        openOnlyAccordion(level) {
            if (!level || !this.openAccordions.hasOwnProperty(level)) {
                return;
            }

            // Create new state with all accordions closed except target
            const newState = {
                customer: false,
                project: false,
                quote: false,
                vendor_quote: false
            };
            newState[level] = true;

            // Atomic update to prevent intermediate "all closed" state
            Object.assign(this.openAccordions, newState);
            this.lastClickedLevel = level;
        },

        /**
         * Utility methods
         */
        formatCurrency(amount) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(amount || 0);
        },

        /**
         * Modal methods
         */
        openModal(type) {
            this.modalType = type;
            this.isEdit = false;
            this.editItemId = null;
            this.validationErrors = {};

            this.initializeModalData(type);
            this.showModal = true;
        },

        openEditModal(type, item) {
            if (!item) return;

            this.modalType = type;
            this.isEdit = true;
            this.editItemId = item.id;
            this.validationErrors = {};

            this.populateModalData(type, item);
            this.showModal = true;
        },

        closeModal() {
            this.showModal = false;
            this.modalType = null;
            this.modalData = {};
            this.isEdit = false;
            this.editItemId = null;
            this.validationErrors = {};
            this.isSubmitting = false;
        },

        handleBackdropClick(event) {
            const modalContent = event.currentTarget.querySelector('.bg-white.rounded-lg.shadow-xl');
            if (modalContent && !modalContent.contains(event.target)) {
                this.closeModal();
            }
        },

        getModalTitle() {
            const titles = {
                customer: this.isEdit ? 'Edit Customer' : 'New Customer',
                project: this.isEdit ? 'Edit Project' : 'New Project',
                quote: this.isEdit ? 'Edit Quote' : 'New Quote',
                'vendor-quote': this.isEdit ? 'Edit Vendor Quote' : 'New Vendor Quote'
            };
            return titles[this.modalType] || (this.isEdit ? 'Edit Item' : 'New Item');
        },

        initializeModalData(type) {
            const today = new Date().toISOString().split('T')[0];

            const defaultData = {
                customer: {
                    name: '',
                    status: 'active',
                    created_date: today
                },
                project: {
                    name: '',
                    budget: 0,
                    status: 'active',
                    start_date: today,
                    customer_id: this.selectedCustomer?.id
                },
                quote: {
                    name: '',
                    amount: 0,
                    status: 'active',
                    valid_until: '',
                    project_id: this.selectedProject?.id
                },
                'vendor-quote': {
                    name: '',
                    vendor_id: null,
                    status: 'active',
                    quoted_amount: 0,
                    priority: 'medium',
                    valid_until: '',
                    tracking_id: '',
                    items_text: '',
                    delivery_requirements: '',
                    is_rush: false,
                    quote_id: this.selectedQuote?.id
                }
            };

            this.modalData = { ...defaultData[type] };
        },

        populateModalData(type, item) {
            const fieldMappings = {
                customer: ['name', 'status', 'created_date'],
                project: ['name', 'budget', 'status', 'start_date', 'customer_id'],
                quote: ['name', 'amount', 'status', 'valid_until', 'project_id'],
                'vendor-quote': ['name', 'vendor_id', 'status', 'quoted_amount', 'priority', 'valid_until', 'tracking_id', 'items_text', 'delivery_requirements', 'is_rush', 'quote_id']
            };

            const fields = fieldMappings[type] || [];
            this.modalData = {};

            fields.forEach(field => {
                this.modalData[field] = item[field] || '';
            });
        },

        /**
         * Form submission and validation
         */
        async submitForm() {
            this.isSubmitting = true;
            this.validationErrors = {};

            try {
                if (!this.validateForm()) {
                    this.isSubmitting = false;
                    return;
                }

                // Prepare data for API submission
                const submissionData = this.prepareSubmissionData();

                const endpoint = this.getApiEndpoint();
                const method = this.isEdit ? 'PUT' : 'POST';
                const url = this.isEdit ? `${endpoint}/${this.editItemId}` : endpoint;

                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(submissionData)
                });

                const result = await response.json();

                if (!response.ok) {
                    if (response.status === 400 && result.detail) {
                        this.validationErrors = this.parseServerError(result.detail);
                        return;
                    }
                    throw new Error(result.detail || `HTTP ${response.status}`);
                }

                // Success - refresh data and close modal
                if (this.isEdit) {
                    await this.refreshDataAfterUpdate(result.data);
                    console.log('Item updated successfully:', result.data);
                } else {
                    await this.refreshDataAfterCreate(result.data);
                    console.log('Item created successfully:', result.data);
                }

                this.closeModal();

            } catch (error) {
                console.error('Error submitting form:', error);
                this.validationErrors = { general: 'Failed to submit. Please try again.' };
            } finally {
                this.isSubmitting = false;
            }
        },

        prepareSubmissionData() {
            // Create a copy of modal data and ensure proper types
            const data = { ...this.modalData };

            // Convert data types for API compatibility
            if (data.vendor_id === '' || data.vendor_id === null || data.vendor_id === undefined) {
                data.vendor_id = null; // Let server validation handle missing vendor
            } else {
                data.vendor_id = parseInt(data.vendor_id, 10);
            }

            
            if (data.customer_id === '' || data.customer_id === null || data.customer_id === undefined) {
                data.customer_id = null;
            } else {
                data.customer_id = parseInt(data.customer_id, 10);
            }

            if (data.project_id === '' || data.project_id === null || data.project_id === undefined) {
                data.project_id = null;
            } else {
                data.project_id = parseInt(data.project_id, 10);
            }

            if (data.quote_id === '' || data.quote_id === null || data.quote_id === undefined) {
                data.quote_id = null;
            } else {
                data.quote_id = parseInt(data.quote_id, 10);
            }

            
            if (data.valid_until === '' || data.valid_until === null || data.valid_until === undefined) {
                data.valid_until = null;
            }

            // Handle budget for projects
            if (data.budget !== undefined) {
                data.budget = parseFloat(data.budget);
            }

            // Handle amount for quotes
            if (data.amount !== undefined) {
                data.amount = parseFloat(data.amount);
            }

            // Handle quoted_amount for vendor quotes
            if (data.quoted_amount !== undefined) {
                data.quoted_amount = parseFloat(data.quoted_amount);
            }

            return data;
        },

        validateForm() {
            const errors = {};
            const data = this.modalData;

            switch(this.modalType) {
                case 'customer':
                    if (!data.name?.trim()) errors.name = 'Name is required';
                    if (!data.created_date) errors.created_date = 'Created date is required';
                    break;
                case 'project':
                    if (!data.name?.trim()) errors.name = 'Name is required';
                    if (!data.budget || data.budget <= 0) errors.budget = 'Budget must be greater than 0';
                    if (!data.start_date) errors.start_date = 'Start date is required';
                    break;
                case 'quote':
                    if (!data.name?.trim()) errors.name = 'Name is required';
                    if (!data.amount || data.amount <= 0) errors.amount = 'Amount must be greater than 0';
                    break;
                case 'vendor-quote':
                    if (!data.name?.trim()) errors.name = 'Name is required';
                    if (!data.vendor_id) errors.vendor_id = 'Vendor is required';
                    if (!data.tracking_id?.trim()) errors.tracking_id = 'Tracking ID is required';
                    if (!data.items_text?.trim()) errors.items_text = 'Items description is required';
                    if (!data.quoted_amount || data.quoted_amount <= 0) errors.quoted_amount = 'Quoted amount must be greater than 0';
                    break;
            }

            this.validationErrors = errors;
            return Object.keys(errors).length === 0;
        },

        parseServerError(detail) {
            if (typeof detail === 'string') {
                return { general: detail };
            }
            return detail;
        },

        getApiEndpoint() {
            const endpoints = {
                'customer': '/api/customers',
                'project': '/api/projects',
                'quote': '/api/quotes',
                'vendor-quote': '/api/vendor-quotes'
            };
            return endpoints[this.modalType];
        },

        /**
         * Data refresh methods
         */
        async refreshDataAfterCreate(newItem) {
            switch(this.modalType) {
                case 'customer':
                    await this.loadCustomers();
                    break;
                case 'project':
                    await this.loadProjects(this.selectedCustomer.id);
                    break;
                case 'quote':
                    await this.loadQuotes(this.selectedProject.id);
                    break;
                case 'vendor-quote':
                    await this.loadVendorQuotes(this.selectedQuote.id);
                    break;
            }
        },

        async refreshDataAfterUpdate(updatedItem) {
            // Update selected item with new data
            switch(this.modalType) {
                case 'customer':
                    if (this.selectedCustomer?.id === updatedItem.id) {
                        this.selectedCustomer = updatedItem;
                    }
                    await this.loadCustomers();
                    break;
                case 'project':
                    if (this.selectedProject?.id === updatedItem.id) {
                        this.selectedProject = updatedItem;
                    }
                    if (this.selectedCustomer) {
                        await this.loadProjects(this.selectedCustomer.id);
                    }
                    break;
                case 'quote':
                    if (this.selectedQuote?.id === updatedItem.id) {
                        this.selectedQuote = updatedItem;
                    }
                    if (this.selectedProject) {
                        await this.loadQuotes(this.selectedProject.id);
                    }
                    break;
                case 'vendor-quote':
                    if (this.selectedVendorQuote?.id === updatedItem.id) {
                        this.selectedVendorQuote = updatedItem;
                    }
                    if (this.selectedQuote) {
                        await this.loadVendorQuotes(this.selectedQuote.id);
                    }
                    break;
            }
        },

        /**
         * Delete methods
         */
        confirmDelete(type, id) {
            if (!id) return;

            const typeLabels = {
                'customer': 'Customer',
                'project': 'Project',
                'quote': 'Quote',
                'vendor-quote': 'Vendor Quote'
            };

            const typeLabel = typeLabels[type] || 'Item';

            // Check for cascade implications
            let cascadeMessage = '';
            if (type === 'customer') {
                cascadeMessage = 'This will also delete all related projects, quotes, and vendor quotes.';
            } else if (type === 'project') {
                cascadeMessage = 'This will also delete all related quotes and vendor quotes.';
            } else if (type === 'quote') {
                cascadeMessage = 'This will also delete all related vendor quotes.';
            }

            if (confirm(`Are you sure you want to delete this ${typeLabel}? ${cascadeMessage}`)) {
                this.deleteItem(type, id);
            }
        },

        async deleteItem(type, id) {
            const originalModalType = this.modalType;
            try {
                // Temporarily set modalType to compute endpoint
                this.modalType = type;
                const endpoint = this.getApiEndpoint();

                const response = await fetch(`${endpoint}/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.detail || `HTTP ${response.status}`);
                }

                await this.refreshDataAfterDelete(type);
                this.clearSelectionsIfDeleted(type, id);

                console.log(`${type} deleted successfully:`, result.message);

            } catch (error) {
                console.error(`Error deleting ${type}:`, error);
                alert(`Failed to delete ${type}. Please try again.`);
            } finally {
                // Always restore original modalType
                this.modalType = originalModalType;
            }
        },

        async refreshDataAfterDelete(type) {
            switch(type) {
                case 'customer':
                    await this.loadCustomers();
                    this.clearSelections();
                    break;
                case 'project':
                    if (this.selectedCustomer) {
                        await this.loadProjects(this.selectedCustomer.id);
                    }
                    this.selectedProject = null;
                    this.selectedQuote = null;
                    this.selectedVendorQuote = null;
                    this.quotes = [];
                    this.vendorQuotes = [];
                    break;
                case 'quote':
                    if (this.selectedProject) {
                        await this.loadQuotes(this.selectedProject.id);
                    }
                    this.selectedQuote = null;
                    this.selectedVendorQuote = null;
                    this.vendorQuotes = [];
                    break;
                case 'vendor-quote':
                    if (this.selectedQuote) {
                        await this.loadVendorQuotes(this.selectedQuote.id);
                    }
                    this.selectedVendorQuote = null;
                    break;
            }
        },

        clearSelectionsIfDeleted(type, deletedId) {
            if (type === 'customer' && this.selectedCustomer?.id === deletedId) {
                this.clearSelections();
            } else if (type === 'project' && this.selectedProject?.id === deletedId) {
                this.selectedProject = null;
                this.selectedQuote = null;
                this.selectedVendorQuote = null;
                this.quotes = [];
                this.vendorQuotes = [];
            } else if (type === 'quote' && this.selectedQuote?.id === deletedId) {
                this.selectedQuote = null;
                this.selectedVendorQuote = null;
                this.vendorQuotes = [];
            } else if (type === 'vendor-quote' && this.selectedVendorQuote?.id === deletedId) {
                this.selectedVendorQuote = null;
            }
        }
    };
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = dataExplorer;
}