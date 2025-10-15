/**
 * Utility functions for the Hierarchical Data Explorer.
 *
 * This module provides common utility functions used across the application
 * including formatting, validation, and helper functions.
 */

/**
 * Format currency values using USD formatting
 * @param {number} amount - The amount to format
 * @returns {string} The formatted currency string
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount || 0);
}

/**
 * Format date strings for display
 * @param {string} dateString - The date string to format
 * @returns {string} The formatted date string
 */
function formatDate(dateString) {
    if (!dateString) return '';
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    } catch (error) {
        return dateString;
    }
}

/**
 * Generate a unique ID for temporary elements
 * @returns {string} A unique identifier
 */
function generateId() {
    return `temp_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
}

/**
 * Debounce function to limit the rate of function execution
 * @param {Function} func - The function to debounce
 * @param {number} delay - The delay in milliseconds
 * @returns {Function} The debounced function
 */
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Deep clone an object to avoid reference issues with circular reference support
 * @param {Object} obj - The object to clone
 * @returns {Object} The cloned object
 */
function deepClone(obj, seen = new WeakMap()) {
    // Handle primitive values and null
    if (obj === null || typeof obj !== 'object') return obj;

    // Handle Date objects
    if (obj instanceof Date) return new Date(obj.getTime());

    // Handle circular references - if we've seen this object before, return the cached clone
    if (seen.has(obj)) {
        return seen.get(obj);
    }

    // Handle arrays
    if (obj instanceof Array) {
        const clonedArray = [];
        seen.set(obj, clonedArray);
        for (let i = 0; i < obj.length; i++) {
            clonedArray[i] = deepClone(obj[i], seen);
        }
        return clonedArray;
    }

    // Handle regular objects
    const clonedObj = {};
    seen.set(obj, clonedObj);

    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            clonedObj[key] = deepClone(obj[key], seen);
        }
    }
    return clonedObj;
}

/**
 * Validate email format
 * @param {string} email - The email to validate
 * @returns {boolean} True if valid email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number format (basic US format)
 * @param {string} phone - The phone number to validate
 * @returns {boolean} True if valid phone format
 */
function isValidPhone(phone) {
    const phoneRegex = /^\(?(\d{3})\)?[-.]?(\d{3})[-.]?(\d{4})$/;
    return phoneRegex.test(phone);
}

/**
 * Parse server error responses into a more usable format
 * @param {Object|string} detail - The error detail from server response
 * @returns {Object} Parsed error object
 */
function parseServerError(detail) {
    if (typeof detail === 'string') {
        return { general: detail };
    }
    return detail || {};
}

/**
 * Get today's date in YYYY-MM-DD format
 * @returns {string} Today's date formatted
 */
function getTodayString() {
    return new Date().toISOString().split('T')[0];
}

/**
 * Check if a value is empty or null/undefined
 * @param {*} value - The value to check
 * @returns {boolean} True if value is empty
 */
function isEmpty(value) {
    return value === null || value === undefined || value === '' ||
           (Array.isArray(value) && value.length === 0) ||
           (typeof value === 'object' && Object.keys(value).length === 0);
}

/**
 * Truncate text to a specified length
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length
 * @param {string} suffix - Suffix to add if truncated (default: '...')
 * @returns {string} The truncated text
 */
function truncateText(text, maxLength, suffix = '...') {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * Capitalize the first letter of each word in a string
 * @param {string} str - The string to capitalize
 * @returns {string} The capitalized string
 */
function capitalizeWords(str) {
    return str.replace(/\b\w/g, char => char.toUpperCase());
}

/**
 * Convert a string to snake_case
 * @param {string} str - The string to convert
 * @returns {string} The snake_case string
 */
function toSnakeCase(str) {
    return str.replace(/\W+/g, ' ')
           .split(/ |\B(?=[A-Z])/)
           .map(word => word.toLowerCase())
           .join('_');
}

/**
 * Convert a string to camelCase
 * @param {string} str - The string to convert
 * @returns {string} The camelCase string
 */
function toCamelCase(str) {
    return str.replace(/_([a-z])/g, (match, letter) => letter.toUpperCase());
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        formatCurrency,
        formatDate,
        generateId,
        debounce,
        deepClone,
        isValidEmail,
        isValidPhone,
        parseServerError,
        getTodayString,
        isEmpty,
        truncateText,
        capitalizeWords,
        toSnakeCase,
        toCamelCase
    };
}