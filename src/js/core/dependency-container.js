/**
 * Dependency Container
 * Manages dependencies between modules (Dependency Injection pattern)
 * This makes modules more testable and loosely coupled
 */

class DependencyContainer {
    constructor() {
        this.dependencies = new Map();
        this.singletons = new Map();
    }

    /**
     * Register a dependency
     * @param {string} name - Dependency name
     * @param {Function|*} factory - Factory function or value
     * @param {boolean} singleton - Whether to create a singleton instance
     */
    register(name, factory, singleton = false) {
        this.dependencies.set(name, { factory, singleton });
    }

    /**
     * Resolve a dependency
     * @param {string} name - Dependency name
     * @returns {*} Resolved dependency
     */
    resolve(name) {
        const dependency = this.dependencies.get(name);
        if (!dependency) {
            throw new Error(`Dependency "${name}" not found`);
        }

        const { factory, singleton } = dependency;

        // If singleton, return cached instance
        if (singleton) {
            if (!this.singletons.has(name)) {
                this.singletons.set(name, typeof factory === 'function' ? factory() : factory);
            }
            return this.singletons.get(name);
        }

        // Otherwise, create new instance
        return typeof factory === 'function' ? factory() : factory;
    }

    /**
     * Check if a dependency is registered
     * @param {string} name - Dependency name
     * @returns {boolean}
     */
    has(name) {
        return this.dependencies.has(name);
    }

    /**
     * Clear all dependencies (useful for testing)
     */
    clear() {
        this.dependencies.clear();
        this.singletons.clear();
    }
}

// Export singleton instance
export const container = new DependencyContainer();

// Export class for testing
export { DependencyContainer };

