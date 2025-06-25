const renderSystem = (entities) => {
    entities.forEach(entity => {
        if (entity.components.renderable && entity.components.position) {
            const { sprite } = entity.components.renderable;
            const { x, y } = entity.components.position;
            sprite.position.set(x, y);
        }
    });
};

const gravitySystem = (entities, delta) => {
    entities.forEach(entity => {
        if (entity.components.velocity) {
            entity.components.position.y += entity.components.velocity.vy * delta;
        }
    });
};
