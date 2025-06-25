const world = {
    entities: [],
    systems: [],
    _nextEntityId: 0,
    createEntity() {
        const entity = { id: this._nextEntityId++, components: {} };
        this.entities.push(entity);
        return entity;
    },
    addComponent(entity, component) {
        entity.components[component.name] = component;
    },
    addSystem(system) {
        this.systems.push(system);
    },
    update(delta) {
        this.systems.forEach(system => system(this.entities, delta));
    }
};
