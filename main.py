from fastapi import FastAPI, Depends, status, Response, HTTPException    
import aioredis
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider

from typing import Optional
from blog import schemas, models
from blog.database import engine, SessionLocal
from sqlalchemy.orm import Session
import uvicorn


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#fastAPI Admin
app.mount("/admin", admin_app)

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close() 


@app.post('/blog', status_code=status.HTTP_201_CREATED)
def create(request: schemas.Blog, db: Session = Depends(get_db)):
	new_blog = models.Blog(title=request.title, body=request.body)
	db.add(new_blog)
	db.commit()
	db.refresh(new_blog) 
	return new_blog

@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT)
def destroy(id, db:Session = Depends(get_db)):
	blog = db.query(models.Blog).filter(models.Blog.id==id)
	if not blog.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id: {id} not available")
	blog.delete(synchronize_session=False)
	db.commit()
	return 'blog deleted'

@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id, request:schemas.Blog, db:Session = Depends(get_db)):
	blog = db.query(models.Blog).filter(models.Blog.id==id)
	if not blog.first():
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id: {id} not available")
	#blog.update(request.dict())
	#or
	blog.update({'title': request.title, 'body': request.body})
	db.commit()
	return 'updated'

@app.get('/blog')
def all(db:Session = Depends(get_db)):
	blogs = db.query(models.Blog).all()
	return blogs

@app.get('/blog/{id}', status_code=200)
def show(id, response:Response, db:Session = Depends(get_db)):
	blog = db.query(models.Blog).filter(models.Blog.id==id).first()
	if not blog:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id: {id} not available")
		#response.status_code = status.HTTP_404_NOT_FOUND
		#return {'detail':f"Blog with id: {id} not available"} 
	return blog



'''
class Blog(Base):
	title: str
	body: str
	published: Optional[bool]

# path parameter: only get 10 published blogs instead of getting all that might cause server downtime 
@app.get('/blog?limit=10&published=true')
def index():
	return {'data':"blog list"}

# query parameter: only get 10 published blogs instead of getting all that might cause server downtime 
# http://localhost:8000/blog1?limit=10&pubished=true
@app.get('/blog1')
def index1(limit = 10, published: bool = True, sort: Optional[str] = None):
	if published:
		return {'data': f'blog list of {limit} published posts'}
	else:
		return {'data': f'blog list of {limit} unpublished posts'}


@app.get('/blog/unpublished')
def unpublished():
	return {'data': 'all unpublished blogs'}

@app.get('/blog/{id}')
def show(id: int):
	# fetch blog id=id
	return {'data':id}

@app.get('blog/{id}comments')
#fetch comments of blog with id = id
def comments(id):
	return {'data': {'1','2'}}

@app.post('/blog')
def create_blog(blog:Blog):
	return {'data': f"blog post title is {blog.title}"}
'''



if __name__ == "__main__":
	uvicorn.run(app, host='127.0.0.1', port=9000)