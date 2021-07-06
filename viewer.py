from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import matplotlib.animation as animation
import sys, time, os, cv2
from PIL import Image
import numpy as np
import curses

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", ".", " "][::-1]

def main():
	def start_curses():
		stdscr = curses.initscr()	# Start the alternate buffer
		curses.curs_set(0)			# Disable cursor
		stdscr.clear()				# Clear the screen
		stdscr.nodelay(True)		# Turn off waiting for a character to be pressed
		curses.noecho()				# Echo no characters on the screen
		curses.cbreak()
		return stdscr


	def update():
	    sys.stdout.write("#")
	    sys.stdout.flush()

	def animate(i):
		axes.view_init(elev=10,azim=i*3.6)
		return axes

	def generate_frame(image, stdscr):
		chars = np.asarray(ASCII_CHARS)
		img, SC, GCF, WCF = image, float(0.15), float(1), 7/4
		S = (round(img.size[0]*SC*WCF), round(img.size[1]*SC))
		img = np.sum(np.asarray(img.resize(S).crop((20, 0, 138, 45))), axis=2)
		img -= img.min()
		img = (1.0 - img/img.max())**GCF*(chars.size-1)
		stdscr.addstr(0,0,"\n".join(("".join(r) for r in chars[img.astype(int)]))) # Print Image onto buffer
		stdscr.refresh()	# Show image
		time.sleep(0.03)	# Wait for 1 frame
		stdscr.clear()

	def make_vid(stdscr):
		try:
			while True:
				cap = cv2.VideoCapture(f"gif/{sys.argv[1][:-4]}.gif")
				while True:
					try:
						ret,frame = cap.read()
						generate_frame(Image.fromarray(frame), stdscr)
						cv2.waitKey(1)
						key = stdscr.getch()
						if str(key) == '113' or str(key) == '27':
							return	# Return if "q" is pressed
					except AttributeError: break
		except KeyboardInterrupt: return


	if os.path.isfile(f'gif/{sys.argv[1][:-4]}.gif'):	# Check if gif is exists
		stdscr = start_curses()
		make_vid(stdscr)
	else:	# Create gif
		print('\033[?25l') # Hide Cursor

		sys.stdout.write("[%s]" % ("-" * 10))	# Loadbar
		sys.stdout.flush()
		sys.stdout.write("\b" * (10+1))

		figure = pyplot.figure(); update()
		axes = mplot3d.Axes3D(figure); update()
		axes.grid(False); update()
		axes._axis3don=False; update()
		your_mesh = mesh.Mesh.from_file(f'models/{sys.argv[1]}'); update()
		axes.add_collection3d(mplot3d.art3d.Poly3DCollection(your_mesh.vectors)); update()
		scale = your_mesh.points.flatten(); update()
		axes.auto_scale_xyz(scale, scale, scale); update()
		ani = animation.FuncAnimation(figure, animate); update()
		ani.save(f'gif/{sys.argv[1][:-4]}.gif',writer='pillow',fps=30); update()

		sys.stdout.write("]\n")

		stdscr = start_curses()
		make_vid(stdscr)


	curses.curs_set(1)
	stdscr.clear()
	stdscr.nodelay(False)
	curses.echo()
	curses.nocbreak()
	curses.endwin()


if __name__ == '__main__':
	main()