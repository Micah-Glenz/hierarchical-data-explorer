/**
 * Reusable UI components for the Hierarchical Data Explorer.
 *
 * This module contains Alpine.js component definitions and reusable
 * UI logic for the application interface.
 */

/**
 * Generic column component for displaying sortable lists of items
 */
function genericColumn() {
    return {
        items: [],
        sortBy: 'name',
        sortOrder: 'asc',

        init() {
            // Items will be set via the :items binding and watch mechanism
        },

        get sortedItems() {
            return [...this.items].sort((a, b) => {
                let aVal = a[this.sortBy] || '';
                let bVal = b[this.sortBy] || '';

                if (typeof aVal === 'string') {
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                }

                if (this.sortOrder === 'asc') {
                    return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                } else {
                    return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
                }
            });
        },

        toggleSort() {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
        }
    };
}

/**
 * Modal component for create/edit forms
 */
function modalComponent() {
    return {
        showModal: false,
        modalType: null,
        modalData: {},
        isEdit: false,
        editItemId: null,
        isSubmitting: false,
        validationErrors: {},

        openModal(type, item = null) {
            this.modalType = type;
            this.isEdit = !!item;
            this.editItemId = item?.id || null;
            this.validationErrors = {};

            if (item) {
                this.populateModalData(type, item);
            } else {
                this.initializeModalData(type);
            }

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
            const modalContent = event.currentTarget.querySelector('.modal-content');
            if (modalContent && !modalContent.contains(event.target)) {
                this.closeModal();
            }
        },

        getModalTitle() {
            const titles = {
                customer: this.isEdit ? 'Edit Customer' : 'New Customer',
                project: this.isEdit ? 'Edit Project' : 'New Project',
                quote: this.isEdit ? 'Edit Quote' : 'New Quote',
                'freight-request': this.isEdit ? 'Edit Freight Request' : 'New Freight Request'
            };
            return titles[this.modalType] || (this.isEdit ? 'Edit Item' : 'New Item');
        },

        initializeModalData(type) {
            const today = new Date().toISOString().split('T')[0];

            const defaultData = {
                customer: {
                    name: '',
                    industry: '',
                    status: 'active',
                    created_date: today
                },
                project: {
                    name: '',
                    budget: 0,
                    status: 'active',
                    start_date: today,
                    customer_id: null
                },
                quote: {
                    name: '',
                    amount: 0,
                    status: 'active',
                    valid_until: '',
                    project_id: null
                },
                'freight-request': {
                    name: '',
                    vendor_id: '',
                    status: 'active',
                    weight: 0,
                    priority: 'medium',
                    estimated_delivery: '',
                    quote_id: null
                }
            };

            this.modalData = { ...defaultData[type] };
        },

        populateModalData(type, item) {
            const fieldMappings = {
                customer: ['name', 'industry', 'status', 'created_date'],
                project: ['name', 'budget', 'status', 'start_date', 'customer_id'],
                quote: ['name', 'amount', 'status', 'valid_until', 'project_id'],
                'freight-request': ['name', 'vendor_id', 'status', 'weight', 'priority', 'estimated_delivery', 'quote_id']
            };

            const fields = fieldMappings[type] || [];
            this.modalData = {};

            fields.forEach(field => {
                this.modalData[field] = item[field] || '';
            });
        },

        validateForm() {
            const errors = {};
            const data = this.modalData;

            switch(this.modalType) {
                case 'customer':
                    if (!data.name?.trim()) errors.name = 'Name is required';
                    if (!data.industry) errors.industry = 'Industry is required';
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
                case 'freight-request':
                    if (!data.name?.trim()) errors.name = 'Name is required';
                    if (!data.vendor_id) errors.vendor_id = 'Vendor is required';
                    if (!data.weight || data.weight <= 0) errors.weight = 'Weight must be greater than 0';
                    break;
            }

            this.validationErrors = errors;
            return Object.keys(errors).length === 0;
        }
    };
}

/**
 * Accordion component for displaying hierarchical details
 */
function accordionComponent() {
    return {
        openAccordions: {
            customer: true,
            project: true,
            quote: true,
            freight: true
        },

        toggleAccordion(section) {
            this.openAccordions[section] = !this.openAccordions[section];
        },

        isAccordionOpen(section) {
            return this.openAccordions[section];
        },

        openAllAccordions() {
            Object.keys(this.openAccordions).forEach(key => {
                this.openAccordions[key] = true;
            });
        },

        closeAllAccordions() {
            Object.keys(this.openAccordions).forEach(key => {
                this.openAccordions[key] = false;
            });
        }
    };
}

/**
 * Loading state manager
 */
function loadingManager() {
    return {
        loading: {
            customers: false,
            projects: false,
            quotes: false,
            freightRequests: false,
            vendors: false
        },

        error: {
            customers: null,
            projects: null,
            quotes: null,
            freightRequests: null,
            vendors: null
        },

        setLoading(type, isLoading) {
            this.loading[type] = isLoading;
        },

        setError(type, error) {
            this.error[type] = error;
        },

        clearError(type) {
            this.error[type] = null;
        },

        clearAllErrors() {
            Object.keys(this.error).forEach(key => {
                this.error[key] = null;
            });
        },

        isLoading(type) {
            return this.loading[type];
        },

        hasError(type) {
            return !!this.error[type];
        }
    };
}

/**
 * Selection manager for hierarchical navigation
 */
function selectionManager() {
    return {
        selectedCustomer: null,
        selectedProject: null,
        selectedQuote: null,
        selectedFreightRequest: null,

        selectCustomer(customer) {
            this.selectedCustomer = customer;
            this.clearLowerSelections('customer');
            return customer;
        },

        selectProject(project) {
            this.selectedProject = project;
            this.clearLowerSelections('project');
            return project;
        },

        selectQuote(quote) {
            this.selectedQuote = quote;
            this.clearLowerSelections('quote');
            return quote;
        },

        selectFreightRequest(freightRequest) {
            this.selectedFreightRequest = freightRequest;
            return freightRequest;
        },

        clearLowerSelections(level) {
            switch(level) {
                case 'customer':
                    this.selectedProject = null;
                    this.selectedQuote = null;
                    this.selectedFreightRequest = null;
                    break;
                case 'project':
                    this.selectedQuote = null;
                    this.selectedFreightRequest = null;
                    break;
                case 'quote':
                    this.selectedFreightRequest = null;
                    break;
            }
        },

        clearAllSelections() {
            this.selectedCustomer = null;
            this.selectedProject = null;
            this.selectedQuote = null;
            this.selectedFreightRequest = null;
        },

        hasSelection(level) {
            switch(level) {
                case 'customer': return !!this.selectedCustomer;
                case 'project': return !!this.selectedProject;
                case 'quote': return !!this.selectedQuote;
                case 'freight': return !!this.selectedFreightRequest;
                default: return false;
            }
        }
    };
}

/**
 * Form validation helper
 */
function formValidator() {
    return {
        validateField(value, rules) {
            const errors = [];

            rules.forEach(rule => {
                switch(rule.type) {
                    case 'required':
                        if (!value || (typeof value === 'string' && !value.trim())) {
                            errors.push(rule.message || 'This field is required');
                        }
                        break;
                    case 'email':
                        if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                            errors.push(rule.message || 'Invalid email format');
                        }
                        break;
                    case 'minLength':
                        if (value && value.length < rule.value) {
                            errors.push(rule.message || `Minimum ${rule.value} characters required`);
                        }
                        break;
                    case 'maxLength':
                        if (value && value.length > rule.value) {
                            errors.push(rule.message || `Maximum ${rule.value} characters allowed`);
                        }
                        break;
                    case 'min':
                        if (value !== undefined && value < rule.value) {
                            errors.push(rule.message || `Value must be at least ${rule.value}`);
                        }
                        break;
                    case 'max':
                        if (value !== undefined && value > rule.value) {
                            errors.push(rule.message || `Value must be at most ${rule.value}`);
                        }
                        break;
                }
            });

            return errors;
        },

        validateForm(formData, schema) {
            const errors = {};

            Object.keys(schema).forEach(field => {
                const fieldErrors = this.validateField(formData[field], schema[field]);
                if (fieldErrors.length > 0) {
                    errors[field] = fieldErrors.join(', ');
                }
            });

            return errors;
        }
    };
}

// Register Alpine.js components
document.addEventListener('alpine:init', () => {
    Alpine.data('genericColumn', genericColumn);
    Alpine.data('modalComponent', modalComponent);
    Alpine.data('accordionComponent', accordionComponent);
    Alpine.data('loadingManager', loadingManager);
    Alpine.data('selectionManager', selectionManager);
    Alpine.data('formValidator', formValidator);
});

// Export components for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        genericColumn,
        modalComponent,
        accordionComponent,
        loadingManager,
        selectionManager,
        formValidator
    };
}