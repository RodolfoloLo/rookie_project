FROM node:20-alpine AS build
WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend .
RUN npm run build

FROM nginx:1.27-alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

#package*.json是一个通配符，表示同时复制package.json和package-lock.json文件，这两个文件分别包含了项目的依赖列表和锁定的依赖版本，使用npm ci命令安装依赖时会根据这两个文件来确保安装的依赖版本与开发环境一致
#复制完项目的依赖列表和锁定的依赖版本,安装完成之后,再复制整个frontend目录,这样可以利用Docker的缓存机制,如果package.json和package-lock.json没有变化,则安装依赖的层可以被缓存,这样在后续修改代码时就不需要重新安装依赖,提高构建效率
#npm run dev是开发模式,会启动一个热重载的开发服务器,适合本地开发调试;npm run build是生产模式,会构建优化后的静态文件,适合部署到生产环境
#使用多阶段构建,第一阶段使用node:20-alpine镜像来构建前端应用,第二阶段使用nginx:1.27-alpine镜像来部署构建好的静态文件,这样可以减小最终镜像的体积,因为nginx镜像只包含了运行nginx所需的文件,而不包含构建工具和源代码
#COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf 这行命令将我们自定义的nginx配置文件复制到nginx镜像中默认的配置目录下,覆盖默认的nginx配置,这样当容器启动时,nginx会使用我们提供的配置来服务静态文件
#COPY --from=build /app/dist /usr/share/nginx/html 这行命令将第一阶段构建生成的静态文件从构建阶段的/app/dist目录复制到nginx镜像中默认的静态文件目录/usr/share/nginx/html,这样当nginx启动时,它会从这个目录提供静态文件服务