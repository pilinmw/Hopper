/**
 * API Communication Module
 * Handles all API requests to the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

const API = {
    /**
     * Upload files to server
     * @param {FileList} files - Files to upload
     * @returns {Promise} Response with task_id
     */
    async uploadFiles(files) {
        const formData = new FormData();
        
        for (let file of files) {
            formData.append('files', file);
        }
        
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        return await response.json();
    },
    
    /**
     * Start merge operation
     * @param {string} taskId - Task ID from upload
     * @param {string} outputFilename - Output file name
     * @returns {Promise} Merge response
     */
    async startMerge(taskId, outputFilename = 'merged_result.xlsx') {
        const response = await fetch(`${API_BASE_URL}/merge`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task_id: taskId,
                output_filename: outputFilename
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Merge failed');
        }
        
        return await response.json();
    },
    
    /**
     * Check task status
     * @param {string} taskId - Task ID
     * @returns {Promise} Task status
     */
    async checkTaskStatus(taskId) {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to get status');
        }
        
        return await response.json();
    },
    
    /**
     * Get download URL for result
     * @param {string} taskId - Task ID
     * @returns {string} Download URL
     */
    getDownloadUrl(taskId) {
        return `${API_BASE_URL}/download/${taskId}`;
    },
    
    /**
     * Check if API is available
     * @returns {Promise<boolean>}
     */
    async checkHealth() {
        try {
            const response = await fetch('http://localhost:8000/api/health');
            return response.ok;
        } catch (error) {
            return false;
        }
    }
};

// Export for use in other modules
window.API = API;
