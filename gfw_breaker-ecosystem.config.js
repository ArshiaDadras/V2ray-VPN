module.exports = {
	apps: [
		{
			name: "GFW-Breaker",
			port: 2500,
			instances: "max",
			exec_mode: "cluster",
			script: "./gfw_breaker.js",
			max_memory_restart: "1G",
			restart_delay: 5000,
			args: "preview",
		  	watch: true,
		}
	]
};
